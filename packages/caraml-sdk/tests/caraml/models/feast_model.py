from caraml.models.model import PyFuncModel


class EchoModel(PyFuncModel):
    def infer(self, request: dict, **kwargs) -> dict:
        return request
