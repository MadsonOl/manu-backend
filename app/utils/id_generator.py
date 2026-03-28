from datetime import datetime
from firebase_admin import firestore


def gerar_id(colecao: str) -> str:
    db = firestore.client()
    agora = datetime.now()
    prefixo = agora.strftime("%Y-%m")

    contador_ref = db.collection("_contadores").document(f"{colecao}_{prefixo}")

    @firestore.transactional
    def incrementar(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if snapshot.exists:
            novo = snapshot.get("valor") + 1
        else:
            novo = 1
        transaction.set(ref, {"valor": novo})
        return novo

    transaction = db.transaction()
    sequencial = incrementar(transaction, contador_ref)
    return f"{prefixo}-{sequencial:04d}"
