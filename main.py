from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from routers import actions,deseq_router
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
    exception_class = exc.__class__.__name__
    headers = {"Access-Control-Allow-Origin": "*"}

    if exception_class == "FileNotFoundError":
        file_name = exc.filename.split('/')
        file_name = file_name[len(file_name) -1]
        return JSONResponse(
            status_code=404,
            content={"message":f"Missing file: {file_name}"},
            headers = headers

        )
    elif exception_class =="UnicornException":
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": f"{exc.details}"},
            headers = headers

        )
    elif exception_class == "KeyError":
        return JSONResponse(
            status_code=404,
            content={"message": f"KeyError could not find {exc.args},please check that the data contains the keys"},
            headers=headers
        )

    elif exception_class == 'RRuntimeError':
        x =exc.args[0]
        message = "R failure in deseq analysis"
        if x.find('some values in assay are not integers') >0:
            message="Deseq analysis must have count values (integers) not float, please upload data according to the instructions"
        elif x.find('ncol(countData) == nrow(colData) is not TRUE')>0:
            message = "Number of columns in count matrix (not include id column) most be equal to design matrix number of rows (not include header)," \
                      " please upload data according to the instructions  "
        return JSONResponse(
            status_code=400,
            content={"message": message},
            headers =headers
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
            headers=headers
        )

@app.get('/')
async def hello_world():
    return {"Hello" : "world1"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)






