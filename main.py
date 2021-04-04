from fastapi import FastAPI
from routers import actions
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException,Request
from fastapi.responses import JSONResponse,PlainTextResponse
from routers import actions,deseq_router, Unicorn_Exception
from routers.Unicorn_Exception import UnicornException
import uvicorn
app = FastAPI()


app.include_router(actions.router)
app.include_router(
    actions.router,
    prefix="/actions",
    tags=["actions"],
)
app.include_router(
    deseq_router.router,
    prefix="/deseq",
    tags=["deseq"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request,exc: Exception):
    print(exc)
    exception_class = exc.__class__.__name__
    if exception_class == "FileNotFoundError":
        return JSONResponse(
            status_code=404,
            content={"message":f"Missing file: {exc.filename}"}
        )
    elif exception_class =="UnicornException":
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": f"{exc.name}, {exc.details}"}
        )
    elif exception_class == "KeyError":
        return JSONResponse(
            status_code=404,
            content={"message": f"KeyError could not find {exc.args},please check that the data contains the keys"}
        )
    elif exception_class == 'RRuntimeError':
        return JSONResponse(
            status_code=400,
            content={"message": "Deseq analysis must have count values (integers) not float, please upload data according to the instructions"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"}
        )

@app.get('/')
async def hello_world():
    return {"Hello" : "world1"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)






