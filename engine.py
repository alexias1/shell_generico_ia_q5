
class Rule:
    def __init__(self, rule_id, conditions, conclusion):
        self.id = rule_id
        self.conditions = list(dict.fromkeys(conditions))
        self.conclusion = conclusion
    def to_dict(self):
        return {"id": self.id, "conditions": self.conditions, "conclusion": self.conclusion}

class KnowledgeBase:
    def __init__(self, facts=None, rules=None):
        self.facts = list(dict.fromkeys(facts or []))
        self.rules = [Rule(r["id"], r["conditions"], r["conclusion"]) for r in (rules or [])]
    @classmethod
    def from_dict(cls, d):
        return cls(d.get("facts", []), d.get("rules", []))
    @classmethod
    def demo(cls):
        return cls(
            ["renda_alta", "garantia_adequada", "historico_bom"],
            [
                {"id":"R1","conditions":["renda_alta","garantia_adequada"],"conclusion":"risco_baixo"},
                {"id":"R2","conditions":["historico_bom","renda_alta"],"conclusion":"cliente_confiavel"},
                {"id":"R3","conditions":["cliente_confiavel","garantia_adequada"],"conclusion":"aprovar_credito"}
            ])
    def to_dict(self):
        return {"facts": self.facts, "rules": [r.to_dict() for r in self.rules]}
    def add_fact(self, x): self.facts.append(x)
    def edit_fact(self, old, new):
        self.facts = [new if x == old else x for x in self.facts]
        for r in self.rules:
            r.conditions = [new if x == old else x for x in r.conditions]
            if r.conclusion == old: r.conclusion = new
    def delete_fact(self, x): self.facts.remove(x)
    def add_rule(self, i, c, out): self.rules.append(Rule(i,c,out))
    def edit_rule(self, old, i, c, out):
        for r in self.rules:
            if r.id == old:
                r.id, r.conditions, r.conclusion = i, list(dict.fromkeys(c)), out
                return
    def delete_rule(self, i): self.rules = [r for r in self.rules if r.id != i]

class InferenceEngine:
    def __init__(self, kb): self.kb = kb

    def run(self, method, goal):
        return {"forward":self.forward, "backward":self.backward, "mixed":self.mixed}[method](goal)

    def forward(self, goal):
        known=set(self.kb.facts); trace=["Forward: início com os fatos conhecidos."]
        changed=True
        while changed:
            changed=False
            for r in self.kb.rules:
                if r.conclusion not in known and all(c in known for c in r.conditions):
                    known.add(r.conclusion); changed=True
                    trace.append(f"Regra {r.id}: condições satisfeitas -> {r.conclusion}.")
        ok=goal in known
        trace.append(f"Resultado: {'objetivo comprovado' if ok else 'objetivo não comprovado'}.")
        return self._result("Forward Chaining",goal,ok,known,trace)

    def backward(self, goal):
        trace=[]; ok, proof=self._prove(goal,set(),trace)
        trace.append(f"Resultado: {'objetivo comprovado' if ok else 'objetivo não comprovado'}.")
        return self._result("Backward Chaining",goal,ok,set(self.kb.facts)|proof,trace)

    def _prove(self, goal, visiting, trace):
        if goal in self.kb.facts:
            trace.append(f"Fato encontrado: {goal}."); return True,{goal}
        if goal in visiting:
            trace.append(f"Ciclo detectado em {goal}."); return False,set()
        visiting.add(goal)
        for r in [x for x in self.kb.rules if x.conclusion == goal]:
            trace.append(f"Tentando {r.id} para provar {goal}.")
            proof=set(); ok=True
            for c in r.conditions:
                good, p=self._prove(c,visiting,trace); proof |= p
                if not good:
                    ok=False; trace.append(f"Condição não comprovada: {c}."); break
            if ok:
                proof.add(goal); trace.append(f"{r.id} satisfeita -> {goal}.")
                visiting.remove(goal); return True,proof
        visiting.remove(goal); return False,set()

    def mixed(self, goal):
        f=self.forward(goal)
        if f["success"]:
            f["method"]="Mixed Chaining"
            f["trace"].insert(1,"Mixed: Forward já comprovou o objetivo; Backward não foi necessário.")
            return f
        b=self.backward(goal)
        return self._result("Mixed Chaining",goal,b["success"],
                            set(f["derived"])|set(b["derived"]),
                            ["Mixed: primeiro Forward; como falhou, iniciou Backward."]+f["trace"]+b["trace"])

    def _result(self, method, goal, ok, derived, trace):
        return {
            "method":method,"goal":goal,"success":ok,"derived":sorted(derived),
            "trace":trace,
            "why": (f"'{goal}' foi comprovado porque as condições necessárias foram satisfeitas."
                    if ok else f"Não foi possível comprovar '{goal}' com os fatos e regras atuais."),
            "how":" → ".join(trace)
        }