# go into this folderpath and run the following in your terminal --> uvicorn main:app

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


data = {
    "id": "123",
    "copper_percentage":0.01
}


@app.get("/copper")
async def read_item():
    return data


@app.post("/copper")
def update_item(id: str = None, copper_percentage: float = 0):
    return {"id": id, "copper_percentage": copper_percentage}

#
# if __name__ == '__main__':
# Starts a new server on localhost:8000.
# Later we can make a config file for this.
#    uvicorn.run(app, host='localhost', port=8000, reload=True)
