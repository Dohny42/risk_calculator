import uvicorn

if __name__ == "__main__":
    uvicorn.run("risk_calculator.api.app:app", host="0.0.0.0", port=8000, reload=True)
