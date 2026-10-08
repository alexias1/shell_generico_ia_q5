
from flask import Flask, jsonify, request, render_template
from pathlib import Path
import json
from engine import KnowledgeBase, InferenceEngine

app=Flask(__name__)
DATA=Path(__file__).parent/"knowledge_base.json"

def kb():
    return KnowledgeBase.from_dict(json.loads(DATA.read_text(encoding="utf-8")))
def save(k):
    DATA.write_text(json.dumps(k.to_dict(),ensure_ascii=False,indent=2),encoding="utf-8")

@app.get("/")
def home(): return render_template("index.html")
@app.get("/api/kb")
def get_kb(): return jsonify(kb().to_dict())

@app.post("/api/facts")
def add_fact():
    d=request.get_json(); x=str(d.get("fact","")).strip(); k=kb()
    if not x:return jsonify(error="Informe o fato."),400
    if x in k.facts:return jsonify(error="Fato já existente."),409
    k.add_fact(x);save(k);return jsonify(k.to_dict()),201

@app.put("/api/facts/<path:old>")
def edit_fact(old):
    x=str(request.get_json().get("fact","")).strip(); k=kb()
    if old not in k.facts:return jsonify(error="Fato não encontrado."),404
    if not x:return jsonify(error="Novo fato inválido."),400
    k.edit_fact(old,x);save(k);return jsonify(k.to_dict())

@app.delete("/api/facts/<path:x>")
def del_fact(x):
    k=kb()
    if x not in k.facts:return jsonify(error="Fato não encontrado."),404
    k.delete_fact(x);save(k);return jsonify(k.to_dict())

@app.post("/api/rules")
def add_rule():
    d=request.get_json(); i=str(d.get("id","")).strip(); c=d.get("conditions",[]); o=str(d.get("conclusion","")).strip(); k=kb()
    if not i or not c or not o:return jsonify(error="ID, condições e conclusão são obrigatórios."),400
    if any(r.id==i for r in k.rules):return jsonify(error="ID de regra já existe."),409
    k.add_rule(i,c,o);save(k);return jsonify(k.to_dict()),201

@app.put("/api/rules/<old>")
def edit_rule(old):
    d=request.get_json(); i=str(d.get("id","")).strip(); c=d.get("conditions",[]); o=str(d.get("conclusion","")).strip(); k=kb()
    if not any(r.id==old for r in k.rules):return jsonify(error="Regra não encontrada."),404
    k.edit_rule(old,i,c,o);save(k);return jsonify(k.to_dict())

@app.delete("/api/rules/<i>")
def del_rule(i):
    k=kb()
    if not any(r.id==i for r in k.rules):return jsonify(error="Regra não encontrada."),404
    k.delete_rule(i);save(k);return jsonify(k.to_dict())

@app.post("/api/infer")
def infer():
    d=request.get_json(); method=d.get("method","forward"); goal=str(d.get("goal","")).strip()
    if method not in ("forward","backward","mixed") or not goal:return jsonify(error="Método ou objetivo inválido."),400
    return jsonify(InferenceEngine(kb()).run(method,goal))

@app.post("/api/reset")
def reset():
    save(KnowledgeBase.demo());return jsonify(kb().to_dict())

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000)