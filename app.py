from flask import Flask, jsonify, request
from PIL import Image
from itertools import groupby
import numpy as np
import tensorflow as tf
from tensorflow import keras
import urllib.request

app = Flask(__name__)
@app.route("/")
def idx():
    return "abcfd"

#Run on http://127.0.0.1:5000

# @app.route("/calculate")
# def apitest():
#     return "API working"

# if __name__ == "__main__":
#   app.run(host="0.0.0.0", debug=False, port=5005)

elements_pred=[]
def calculate(img_loc):
    global elements_pred
    'loading image'
    urllib.request.urlretrieve(img_loc,"input.png")
    image = Image.open("input.png").convert("L")
    image.show()

    'resizing to 28 height pixels'
    w = image.size[0]
    h = image.size[1]
    r = w / h # aspect ratio
    new_w = int(r * 28)
    new_h = 28
    new_image = image.resize((new_w, new_h))

    'converting to a numpy array'
    new_image_arr = np.array(new_image)

    'inverting the image to make background = 0'
    new_inv_image_arr = 255 - new_image_arr

    'rescaling the image'
    final_image_arr = new_inv_image_arr / 255.0

    'splitting image array into individual digit arrays using non zero columns'
    m = final_image_arr.any(0)
    out = [final_image_arr[:,[*g]] for k, g in groupby(np.arange(len(m)), lambda x: m[x] != 0) if k]


    '''
    iterating through the digit arrays to resize them to match input 
    criteria of the model = [mini_batch_size, height, width, channels]
    '''
    num_of_elements = len(out)
    elements_list = []

    for x in range(0, num_of_elements):

        img = out[x]
        
        #adding 0 value columns as fillers
        width = img.shape[1]
        filler = (final_image_arr.shape[0] - width) / 2
        
        if filler.is_integer() == False:    #odd number of filler columns
            filler_l = int(filler)
            filler_r = int(filler) + 1
        else:                               #even number of filler columns
            filler_l = int(filler)
            filler_r = int(filler)
        
        arr_l = np.zeros((final_image_arr.shape[0], filler_l)) #left fillers
        arr_r = np.zeros((final_image_arr.shape[0], filler_r)) #right fillers
        
        #concatinating the left and right fillers
        help_ = np.concatenate((arr_l, img), axis= 1)
        element_arr = np.concatenate((help_, arr_r), axis= 1)
        
        element_arr.resize(28, 28, 1) #resize array 2d to 3d

        #storing all elements in a list
        elements_list.append(element_arr)


    elements_array = np.array(elements_list)

    'reshaping to fit model input criteria'
    elements_array = elements_array.reshape(-1, 28, 28, 1)

    'predicting using the model'
    #model = keras.models.load_model("C:\\Users\\Priyam_Shukla\\Downloads\\Final Year Project\\model1")
    model = keras.models.load_model("model1")
    elements_pred =  model.predict(elements_array)
    elements_pred = np.argmax(elements_pred, axis = 1)
    print(elements_pred)

def math_expression_generator(arr):
    
    op = {
              10,   # = "/"
              11,   # = "+"
              12,   # = "-"
              13    # = "*"
                  }   
    
    m_exp = []
    temp = []
        
    'creating a list separating all elements'
    for item in arr:
        if item not in op:
            temp.append(item)
        else:
            m_exp.append(temp)
            m_exp.append(item)
            temp = []
    if temp:
        m_exp.append(temp)
        
    'converting the elements to numbers and operators'
    i = 0
    num = 0
    for item in m_exp:
        if type(item) == list:
            if not item:
                m_exp[i] = ""
                i = i + 1
            else:
                num_len = len(item)
                for digit in item:
                    num_len = num_len - 1
                    num = num + ((10 ** num_len) * digit)
                m_exp[i] = str(num)
                num = 0
                i = i + 1
        else:
            m_exp[i] = str(item)
            m_exp[i] = m_exp[i].replace("10","/")
            m_exp[i] = m_exp[i].replace("11","+")
            m_exp[i] = m_exp[i].replace("12","-")
            m_exp[i] = m_exp[i].replace("13","*")
            
            i = i + 1
    
    
    'joining the list of strings to create the mathematical expression'
    separator = ' '
    m_exp_str = separator.join(m_exp)
    
    return (m_exp_str)


@app.route("/func", methods = ['POST'])

def func(): 
    'creating the mathematical expression'
    with app.app_context():
        #test code
        image_loc = request.form.get('image_url')
        calculate(image_loc)
        m_exp_str = math_expression_generator(elements_pred)

    'calculating the mathematical expression using eval()'
    while True:
        try:
            answer = eval(m_exp_str)    #evaluating the answer
            answer = round(answer, 2)
            equation  = m_exp_str + " = " + str(answer)
            print(equation)   #printing the equation
            result={"answer":equation}
            return jsonify(result)
            #break

        except SyntaxError:
            print("Invalid predicted expression!!")
            print("Following is the predicted expression:")
            print(m_exp_str)
            break

#print(func())

# if __name__=="__main__":
#     app.run(debug=True)
