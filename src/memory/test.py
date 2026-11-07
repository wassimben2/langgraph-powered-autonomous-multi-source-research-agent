from memory.vector_store import vector_store

data = vector_store.get()
ids = data["ids"]

if ids:
    vector_store.delete(ids=ids)
    print(f"{len(ids)} memories deleted.")
else:
    print("Memory is already empty.")