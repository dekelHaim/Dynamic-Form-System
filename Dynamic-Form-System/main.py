def run_api():
    print("\n✅ Starting FastAPI server...")
    import uvicorn
    uvicorn.run(
        "app.services.api.gateway:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

def main():
    run_api()

if __name__ == "__main__":
    main()
