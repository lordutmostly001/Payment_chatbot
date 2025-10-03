from vector_db.vector_search import vector_search

vector_search.index.delete(delete_all=True)
print("All vectors deleted")