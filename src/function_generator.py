import re

"""
Generate OpenAI function specifications and Boto3 functions using a Smithy model.
"""
class FunctionGenerator:
    def __init__(self, model = {}) -> None:
        self.model = model

    """
    Given a function name and an output destination, generate an OpenAI function specification
    using the Smithy model and return it in dictionary format.
    """
    def generate_function_specification(self, function_name):            
        # parse the model
        operation = { k:v for k, v in self.model["shapes"].items() if v["type"] == "operation" and k.split("#")[-1] == function_name}
        if len(operation) != 1:
            raise Exception(f"Failed to find the function named {function_name} in the model.")    
        operation_name = list(operation.keys())[0]
        operation = operation[operation_name]

        # initialize function specification
        function = {
            "name": operation_name.split("#")[-1]
        }

        # fill in description if documentation exists
        traits = operation.get("traits")    
        if traits:
            documentation = operation.get("traits").get("smithy.api#documentation")
            if documentation:
                function["description"] = self.clean_documentation(documentation)

        parameters = {
            "type": "object"
        }
        properties = {}
        required = []

        if operation["input"]["target"] == "smithy.api#Unit":
            parameters["properties"] = properties
            parameters["required"] = required
        else:
            input_target = operation["input"]["target"]
            input = model["shapes"][input_target]
            for member in input["members"]:
                member_type = model["shapes"][input["members"][member]["target"]]["type"]
                member_properties = {
                    "type": member_type  # TODO handle complex types like array, enum, etc.
                }

                member_traits = input["members"][member].get("traits")
                if member_traits:
                    documentation = member_traits.get("smithy.api#documentation")
                    if documentation:
                        member_properties["description"] = self.clean_documentation(documentation)

                    member_required = member_traits.get("smithy.api#required")
                    if member_required is not None:
                        required.append(member)
                        
                properties[member] = member_properties

            parameters["properties"] = properties
            parameters["required"] = required

        function["parameters"] = parameters
        return function

    def clean_documentation(self, string):
        TAGS_REGEX = re.compile('<.*?>') 
        WHITESPACE_REGEX = re.compile('\s+')
        string = re.sub(TAGS_REGEX, '', string)  # Remove HTML tags in documentation like <p>, <a>, etc.
        string = re.sub(WHITESPACE_REGEX, ' ', string)  # Replace all more-than-one spaces with just one space
        # TODO is truncation required?
        return string.replace("\n", "").replace("\t", "")[:200] # Remove newlines, tabs

    """
    Given a function name and a set of AWS credentials, generate an in-memory function 
    which uses boto3 to make the actual request to AWS.
    """
    def generate_function(self, function_name, credentials = {}):
        if not credentials.get("AWS_ACCESS_KEY_ID") or not credentials.get("AWS_SECRET_ACCESS_KEY"):
            raise Exception("Received invalid credentials, it must be a dictionary with the keys AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")

        def function(arguments):
            return "Hello!"
            # client = boto3.blablabla(credentials = credentials)
            # return client.function_name(**arguments)
        
        return function
    
if __name__ == "__main__":
    import json
    model = json.loads(open("./s3.json", "r").read())
    generator = FunctionGenerator(model)

    spec = generator.generate_function_specification("CreateBucket")
    print(spec)
