"""WebSocket streaming for real-time monitoring"""

from flask_socketio import SocketIO, emit
from typing import Optional

# Global SocketIO instance
socketio: Optional[SocketIO] = None


def init_socketio(app) -> SocketIO:
    """Initialize SocketIO with Flask app

    Args:
        app: Flask application

    Returns:
        SocketIO instance
    """
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading'
    )

    # Register event handlers
    @socketio.on('connect', namespace='/monitoring')
    def handle_connect():
        print('Client connected to monitoring stream')
        emit('connected', {'status': 'connected'})

    @socketio.on('disconnect', namespace='/monitoring')
    def handle_disconnect():
        print('Client disconnected from monitoring stream')

    @socketio.on('subscribe', namespace='/monitoring')
    def handle_subscribe(data):
        """Subscribe to specific trace categories"""
        categories = data.get('categories', [])
        print(f'Client subscribed to categories: {categories}')
        emit('subscribed', {'categories': categories})

    return socketio


def broadcast_trace(trace: dict):
    """Broadcast a new trace to all connected clients

    Args:
        trace: Trace dictionary to broadcast
    """
    if socketio:
        socketio.emit('new_trace', trace, namespace='/monitoring')


def broadcast_alert(alert: dict):
    """Broadcast an anomaly alert to all connected clients

    Args:
        alert: Alert dictionary to broadcast
    """
    if socketio:
        socketio.emit('new_alert', alert, namespace='/monitoring')


def broadcast_metrics(metrics: dict):
    """Broadcast aggregated metrics to all connected clients

    Args:
        metrics: Metrics dictionary to broadcast
    """
    if socketio:
        socketio.emit('metrics_update', metrics, namespace='/monitoring')


def get_socketio() -> Optional[SocketIO]:
    """Get the SocketIO instance

    Returns:
        SocketIO instance or None if not initialized
    """
    return socketio
