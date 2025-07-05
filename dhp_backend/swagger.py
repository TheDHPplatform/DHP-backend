from drf_yasg.generators import OpenAPISchemaGenerator

class PathBasedTagSchemaGenerator(OpenAPISchemaGenerator):
    def get_paths_object(self, paths=None):
        paths = super().get_paths_object(paths)

        # Inject tags based on second URL segment
        for path, path_item in paths.items():
            segments = path.strip("/").split("/")
            tag = segments[1] if len(segments) > 1 else segments[0]  # use second segment, fallback to first

            for method in path_item:  # path_item is a dict-like object of operations
                operation = path_item[method]
                if(type(operation) == list):
                    continue
                if not operation.get("tags"):
                    operation["tags"] = [tag.capitalize()]  # optional formatting
        return paths
