def carregar_empresas(db, empresa_ids) -> dict:
    # Le em uma unica passada (db.get_all) apenas as empresas referenciadas pelas
    # ordens, evitando uma leitura por OS (N+1). Empresas ausentes ou inexistentes
    # simplesmente nao entram no mapa, o que mantem o comportamento de empresa=None
    # nesses casos. Compartilhado entre a listagem de ordens e o relatorio.
    ids_unicos = {eid for eid in empresa_ids if eid}
    if not ids_unicos:
        return {}
    refs = [db.collection("empresas").document(eid) for eid in ids_unicos]
    return {
        snap.id: {"id": snap.id, **snap.to_dict()}
        for snap in db.get_all(refs)
        if snap.exists
    }
