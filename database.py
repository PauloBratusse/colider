from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Simulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(10), nullable=False)  # v1 ou v2
    num_particles = db.Column(db.Integer, nullable=False)
    num_steps = db.Column(db.Integer, nullable=False)
    delta = db.Column(db.Float, nullable=False)
    velocity_coefficient = db.Column(db.Float, nullable=False)
    box_width = db.Column(db.Float)
    box_height = db.Column(db.Float)
    box_depth = db.Column(db.Float)
    image_path = db.Column(db.String(500))
    animation_path = db.Column(db.String(500), nullable=False)  # novo campo para animação
    status = db.Column(db.String(20), default='completed')  # completed, failed, pending
    error_message = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    execution_time = db.Column(db.Float)  # tempo em segundos

    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'num_particles': self.num_particles,
            'num_steps': self.num_steps,
            'delta': self.delta,
            'velocity_coefficient': self.velocity_coefficient,
            'box_width': self.box_width,
            'box_height': self.box_height,
            'box_depth': self.box_depth,
            'image_path': self.image_path,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'execution_time': self.execution_time
        }
