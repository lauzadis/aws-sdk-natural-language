from txtai.embeddings import Embeddings


class Searcher:
    def __init__(self) -> None:
        self.embeddings = Embeddings({"path": "../all-mpnet-base-v2"})
        self.data = {}

    def update(self, data) -> None:
        self.data.update(data)

    def get_data(self) -> map:
        return self.data
    
    """
    Runs similarity searches on the keys of a given map, returning the map value of the closest match
    Example:
        data: {
            "animal with four legs that barks a lot": "dog",
            "animal with four legs that meows": "cat"
        }
        query: "what is an animal that barks a lot?"
        result: "dog"
    """
    def search(self, query) -> str:
        keys = list(self.data.keys())
        result = self.embeddings.similarity(query, keys)
        return self.data[keys[result[0][0]]]
    

if __name__ == "__main__":
    lookup = {
        "Put an object": "PutObjectRequest",
        "Download an object": "GetObjectRequest",
        "Delete an object": "DeleteObjectRequest",
        "Create a bucket": "CreateBucketRequest",
        "Delete a bucket": "DeleteBucketRequest"
    }

    searcher = Searcher()
    searcher.update(lookup)

    query = 'Can you help me create a bucket named "test-bucket".'
    print(searcher.search(query))
