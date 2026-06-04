from fastapi import HTTPException

from app.utils.id_generator import gerar_id


class CrudRepository:
    """CRUD generico sobre uma colecao do Firestore.

    Encapsula o padrao repetido nos routers (criar com ID sequencial, listar,
    obter/atualizar/excluir com checagem de existencia) numa unica implementacao.
    As mensagens de 404 e de exclusao sao injetadas por router porque fazem parte
    do contrato da API (genero e substantivo variam: empresa/ordem -> "encontrada",
    chamado/profissional -> "encontrado"). O nome da colecao tambem e a chave do
    gerador de IDs (gerar_id), entao um valor so serve para os dois.
    """

    def __init__(self, colecao: str, *, nao_encontrado: str, excluido: str):
        self.colecao = colecao
        self.nao_encontrado = nao_encontrado
        self.excluido = excluido

    def _ref(self, db, item_id: str):
        return db.collection(self.colecao).document(item_id)

    def _exigir(self, ref):
        # Centraliza o 404 com a mensagem exata esperada pelo contrato.
        if not ref.get().exists:
            raise HTTPException(status_code=404, detail=self.nao_encontrado)

    def criar(self, db, data: dict) -> dict:
        novo_id = gerar_id(self.colecao)
        registro = {**data, "id": novo_id}
        self._ref(db, novo_id).set(registro)
        return registro

    def listar(self, db) -> list[dict]:
        return [{"id": doc.id, **doc.to_dict()} for doc in db.collection(self.colecao).stream()]

    def obter(self, db, item_id: str) -> dict:
        # Uma unica leitura: busca e valida a existencia no mesmo get.
        doc = self._ref(db, item_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=self.nao_encontrado)
        return {"id": doc.id, **doc.to_dict()}

    def atualizar(self, db, item_id: str, data: dict) -> dict:
        ref = self._ref(db, item_id)
        self._exigir(ref)
        ref.update(data)
        atualizado = ref.get()
        return {"id": atualizado.id, **atualizado.to_dict()}

    def excluir(self, db, item_id: str) -> dict:
        ref = self._ref(db, item_id)
        self._exigir(ref)
        ref.delete()
        return {"message": self.excluido}
