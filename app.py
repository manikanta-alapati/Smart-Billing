from flask import Flask, render_template, request
import cv2
import numpy as np
import glob
import random
import base64

app = Flask(__name__)


net = cv2.dnn.readNet("mega_final_product.weights", "final_product.cfg")


classes = open("classes.txt").read().split("\n")

database = {
                "aashirvaad": { "cost": 100, "name": "Aashirvaad Atta 1 Kg"},
                "boost": { "cost": 5, "name": "Boost Packet"},
                "dabur_red_paste": { "cost": 20, "name": "Dabur Red Paste"},
                "oorvasi": { "cost": 5, "name": "Oorvasi Soap"},
                "santoor": { "cost": 30, "name": "Santoor Soap"},
                "surf_excel": { "cost": 26, "name": "Surf Excel Soap"},
                "tata_salt": { "cost": 20, "name": "Tata Salt Packet"},
                "yippee": { "cost": 5, "name": "Yippee Noodles"},
                
        }



layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))


def get_predictions(image_path):

	img = cv2.imread("static/images/sample.jpg")
	
	h, w, ch = img.shape 
	"""
	factor = 416/min(w, h)

	img = cv2.resize(img, (int(w*factor), int(h*factor)))

	h, w, ch = img.shape
	
	l = max(0, w//2-208)
	r = min(w, l+416)
	t = max(0, h//2-208)
	b = min(h, t+416)
	
	img = img[t:b, l:r]
	"""
	factor = 416/max(w, h)

	img = cv2.resize(img, (int(w*factor), int(h*factor)))

	sh, sw, sch = img.shape


	white_image = np.zeros([416,416,3],dtype=np.uint8)
	white_image.fill(255)

	t=max(208-sh//2, 0)

	l= max(208-sw//2, 0)

	white_image[t:t+sh, l:l+sw] = img

	img = white_image

	height, width, channels = img.shape

	
		
	blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

	net.setInput(blob)
	outs = net.forward(output_layers)

		
	class_ids = []
	confidences = []
	boxes = []
	for out in outs:
		for detection in out:
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]
			if confidence > 0.5:
				
				print(class_id)
				center_x = int(detection[0] * width)
				center_y = int(detection[1] * height)
				w = int(detection[2] * width)
				h = int(detection[3] * height)
				
				x = int(center_x - w / 2)
				y = int(center_y - h / 2)

				boxes.append([x, y, w, h])
				confidences.append(float(confidence))
				class_ids.append(class_id)

	indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.1)
	main_classes = []
	font = cv2.FONT_HERSHEY_PLAIN
	for i in range(len(boxes)):
		if i in indexes:
			x, y, w, h = boxes[i]
			label = str(classes[class_ids[i]])
			color = colors[class_ids[i]]
			cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
			cv2.putText(img, label, (x, y + 30), font, 2, color, 2)
			main_classes.append(class_ids[i])


	img = img[t:t+sh, l:l+sw]

	cv2.imwrite("static/images/output.jpg", img)
	print(main_classes)
	return main_classes

@app.route('/', methods=["GET", "POST"])
def home():
	if request.method == "GET":
		return render_template('index.html', strings={}, total_cost=0, post=False)
	try:
		sample_file_path = "static/images/sample.jpg"
		
		image_data = request.form.get("image-data")

		image = open(sample_file_path, "wb")

		image.write(base64.b64decode((image_data)))

		image.close()

		file = request.files["input_image"]
		if file.filename!='':
			file.save(sample_file_path)
			print('file is uploaded')

		class_ids = get_predictions(sample_file_path)
		total_cost = 0
		counts = dict()
		for class_id in class_ids:
			product = classes[class_id]
			total_cost+=database[product]["cost"]
			if product not in counts:
				counts[product]=0
			counts[product] += 1
		strings = {product:{"cost": f"{counts[product]} * Rs {database[product]['cost']}", "name":database[product]["name"]} for product in counts}
		return render_template("index.html", strings=strings, total_cost=total_cost, post=True)
	except Exception as err:
		print(err)
		#return str(err)
		return render_template('index.html', strings={}, total_cost=0, get=True)


@app.route('/products', methods=['GET'])
def products():
	return render_template('products.html', products={product:database[product]["name"] for product in database})

#app.run()
