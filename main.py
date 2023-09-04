import flask
from waitress import serve
from flask import Flask, request, jsonify
from preprocessing import ner_eng, ner_chin, engzh_separation
from ascii_art import husky_art

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/ner_detect", methods=["POST"])
def ner_detect():
    raw_sent = str(request.json['sent'])
    engwds, chinwds = engzh_separation(raw_sent)
    pred_eng = ner_eng("model/en_md_221", engwds)
    pred_chin = ner_chin("model/zh_bl_144", chinwds)
    return jsonify({'results':[pred_chin, pred_eng]})

# curl -v -X POST -H "Content-Type: application/json" -d '{"sent": "Mike gonna hiking during the T8 with Stephen."}' http://localhost:8000/ner_detect
# curl -v -X POST -H "Content-Type: application/json" -d '{"sent": "Weekend同啊Mike有咩玩？我地想去disneyland同海洋公園，嗰道有無性價比高嘅高級米其林餐廳？我地想食鵝肝，caviars同黑松露。"}' http://localhost:8000/ner_detect

print("'Husky is soooooo cute.'")
print(husky_art())
if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8000)
