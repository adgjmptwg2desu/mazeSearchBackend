from typing import Literal

from pydantic import BaseModel, Field, model_validator

CellType = Literal["wall", "path", "start", "goal"]


class Position(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class MazeRequest(BaseModel):
    cells: list[list[CellType]] = Field(min_length=1)
    startPosition: Position
    goalPosition: Position

    @model_validator(mode="after")
    def validate_maze(self):
        width = len(self.cells[0])
        if width == 0 or any(len(row) != width for row in self.cells):
            raise ValueError("Maze cells must be a non-empty rectangular grid")

        height = len(self.cells)
        for label, position in (
            ("startPosition", self.startPosition),
            ("goalPosition", self.goalPosition),
        ):
            if position.x >= width or position.y >= height:
                raise ValueError(f"{label} is outside the maze")
            if self.cells[position.y][position.x] == "wall":
                raise ValueError(f"{label} cannot be on a wall")

        return self


class SearchTreeNode(BaseModel):
    id: str
    label: str
    position: Position
    parentId: str | None
    depth: int
    visited: bool
    onPath: bool


class SearchTreeState(BaseModel):
    nodes: list[SearchTreeNode]
    activeNodeIds: list[str]
    pathNodeIds: list[str]


class SearchResponse(BaseModel):
    found: bool
    state: SearchTreeState
