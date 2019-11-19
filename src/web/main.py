import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from definitions import PATH_DATA_DIRECTORY
from src.cu_estimator import CuEstimator
from src.data_loader import DataLoader
from src.yield_estimator import YieldEstimator

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http:localhost",
    "http:localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_loader = DataLoader(os.path.join(PATH_DATA_DIRECTORY, '1'))

yield_estimator = YieldEstimator()
yield_estimator.fit(data_loader.df_previous_production)

cu_estimator = CuEstimator()
cu_estimator.fit(data_loader.df_previous_production)


@app.get("/")
def test_data():
    return {
        'x': ['giraffes', 'orangutans', 'monkeys'],
        'y': [20, 14, 23],
    }


@app.get('/plots/yield')
def get_yield_data():
    results = {}
    for steel_grade in ['ST1', 'ST2', 'ST3']:
        grade_yield = yield_estimator.get_estimated_values(steel_grade)

        results.update({steel_grade: {
            'x': list(grade_yield.keys()),
            'y': list(grade_yield.values())
        }})
    return results


@app.get('/plots/copper')
def get_yield_data():
    results = {}
    for steel_grade in ['ST1', 'ST2', 'ST3']:
        grade_yield = cu_estimator.get_estimated_values(steel_grade)

        results.update({steel_grade: {
            'x': list(grade_yield.keys()),
            'y': list(grade_yield.values())
        }})
    return results


@app.get('/plots/inventory')
def get_inventory_data():
    data = data_loader.scrap_inventory
    return {
        'values': list(data.values()),
        'labels': list(data.keys())
    }


@app.get('/plots/prices')
def get_prices_data():
    data = data_loader.scrap_prices
    return data


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
