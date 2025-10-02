from dataclasses import dataclass


@dataclass
class GroqListModelsResponse:
    @dataclass
    class Details:
        family: str
        version: str
        size: str
        sequence_length: str
        tag: str
        name: str
        owner: str

    @dataclass
    class Meta:
        created: int

    id: str
    details: Details
    meta: Meta
    status: str
