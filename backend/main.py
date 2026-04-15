print(f"🚀 Starting server at http://{Config.HOST}:{Config.PORT}")
    print("=" * 60)
    
    # Run server
    app.socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False,  # Disable reloader to avoid double sync threads
        allow_unsafe_werkzeug=True  # Allow production use
    )
    
    # Cleanup
    app.sync_service.stop()
