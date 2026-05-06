from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from datetime import datetime
from database import db, Simulation

# Importar módulos de simulação
import colider
import colider_v2

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///colider_simulations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Criar diretórios necessários
os.makedirs('static/animations', exist_ok=True)

@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()

def generate_animation_v1(particles, frontier, num_steps, delta, animation_path):
    """Gera animação 3D para simulação v1"""
    try:
        # Simulação com armazenamento de posições
        positions_history = []
        particles_copy = [colider.Particle(p.x, p.y, p.z, p.vx, p.vy, p.vz, p.radius) for p in particles]
        
        # Armazenar posição inicial
        positions_step = [(p.x, p.y, p.z) for p in particles_copy]
        positions_history.append(positions_step)
        
        # Executar simulação e armazenar posições
        for step in range(min(50, num_steps)):  # Limitar a 50 frames para não ficar muito pesado
            for i in range(len(particles_copy)):
                colider.temporal_step(delta, i, particles_copy, frontier)
            positions_step = [(p.x, p.y, p.z) for p in particles_copy]
            positions_history.append(positions_step)
        
        # Criar figura 3D
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Função para atualizar frame
        def update_frame(frame):
            ax.clear()
            
            if frame < len(positions_history):
                positions = positions_history[frame]
                x_data = [p[0] for p in positions]
                y_data = [p[1] for p in positions]
                z_data = [p[2] for p in positions]
                
                ax.scatter(x_data, y_data, z_data, c='red', marker='o', s=50)
            
            ax.set_xlim(0, frontier.xf)
            ax.set_ylim(0, frontier.yf)
            ax.set_zlim(0, frontier.zf)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'Colider V1 - Frame {frame}/{len(positions_history)-1}')
        
        # Criar animação
        anim = animation.FuncAnimation(fig, update_frame, frames=len(positions_history), 
                                       interval=100, repeat=True)
        
        # Salvar como GIF
        writer = PillowWriter(fps=10)
        anim.save(animation_path, writer=writer)
        plt.close(fig)
        
        return True
    except Exception as e:
        print(f"Erro ao gerar animação v1: {e}")
        return False

def generate_animation_v2(particles, num_steps, delta, animation_path):
    """Gera animação 3D para simulação v2"""
    try:
        # Simulação com armazenamento de posições
        positions_history = []
        particles_copy = [colider_v2.Particle(p.x, p.y, p.z, p.vx, p.vy, p.vz, p.radius) for p in particles]
        mesh = colider_v2.create_box_mesh(10, 10, 10)
        
        # Armazenar posição inicial
        positions_step = [(p.x, p.y, p.z) for p in particles_copy]
        positions_history.append(positions_step)
        
        # Executar simulação e armazenar posições
        for step in range(min(50, num_steps)):  # Limitar a 50 frames
            for i in range(len(particles_copy)):
                particles_copy[i].step(delta, mesh)
            positions_step = [(p.x, p.y, p.z) for p in particles_copy]
            positions_history.append(positions_step)
        
        # Criar figura 3D
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Função para atualizar frame
        def update_frame(frame):
            ax.clear()
            
            if frame < len(positions_history):
                positions = positions_history[frame]
                x_data = [p[0] for p in positions]
                y_data = [p[1] for p in positions]
                z_data = [p[2] for p in positions]
                
                ax.scatter(x_data, y_data, z_data, c='blue', marker='o', s=50)
            
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.set_zlim(0, 10)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'Colider V2 - Frame {frame}/{len(positions_history)-1}')
        
        # Criar animação
        anim = animation.FuncAnimation(fig, update_frame, frames=len(positions_history), 
                                       interval=100, repeat=True)
        
        # Salvar como GIF
        writer = PillowWriter(fps=10)
        anim.save(animation_path, writer=writer)
        plt.close(fig)
        
        return True
    except Exception as e:
        print(f"Erro ao gerar animação v2: {e}")
        return False

@app.route('/')
def index():
    """Página principal com opções de simulação"""
    return render_template('index.html')

@app.route('/api/simulate/v1', methods=['POST'])
def simulate_v1():
    """Executa simulação v1"""
    try:
        data = request.get_json()
        
        num_particles = int(data.get('num_particles', 10))
        num_steps = int(data.get('num_steps', 100))
        delta = float(data.get('delta', 0.01))
        velocity_coef = float(data.get('velocity_coefficient', 1.0))
        box_width = float(data.get('box_width', 10.0))
        box_height = float(data.get('box_height', 10.0))
        box_depth = float(data.get('box_depth', 10.0))
        
        start_time = time.time()
        
        # Inicializar simulação
        particles, frontier = colider.init_sim(
            quantity=num_particles,
            cx=box_width,
            cy=box_height,
            cz=box_depth,
            vel_col=velocity_coef
        )
        
        # Executar simulação
        for step in range(num_steps):
            for i in range(len(particles)):
                colider.temporal_step(delta, i, particles, frontier)
        
        execution_time = time.time() - start_time
        
        # Gerar animação
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        animation_filename = f"colider_v1_{timestamp}.gif"
        animation_path = os.path.join('static/animations', animation_filename)
        
        if generate_animation_v1(particles, frontier, num_steps, delta, animation_path):
            # Salvar no banco de dados
            simulation = Simulation(
                version='v1',
                num_particles=num_particles,
                num_steps=num_steps,
                delta=delta,
                velocity_coefficient=velocity_coef,
                box_width=box_width,
                box_height=box_height,
                box_depth=box_depth,
                animation_path=f'/static/animations/{animation_filename}',
                status='completed',
                execution_time=execution_time
            )
            db.session.add(simulation)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Simulação V1 concluída com sucesso',
                'animation_path': f'/static/animations/{animation_filename}',
                'execution_time': round(execution_time, 2),
                'simulation_id': simulation.id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao gerar animação'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na simulação V1: {str(e)}'
        }), 500

@app.route('/api/simulate/v2', methods=['POST'])
def simulate_v2():
    """Executa simulação v2"""
    try:
        data = request.get_json()
        
        num_particles = int(data.get('num_particles', 10))
        num_steps = int(data.get('num_steps', 100))
        delta = float(data.get('delta', 0.01))
        velocity_coef = float(data.get('velocity_coefficient', 1.0))
        
        start_time = time.time()
        
        # Inicializar simulação v2
        particles = colider_v2.init_sim(
            quantity=num_particles,
            vel_col=velocity_coef
        )
        
        # Criar mesh (caixa)
        mesh = colider_v2.create_box_mesh(10, 10, 10)
        
        # Executar simulação
        for step in range(num_steps):
            for i in range(len(particles)):
                particles[i].step(delta, mesh)
        
        execution_time = time.time() - start_time
        
        # Gerar animação
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        animation_filename = f"colider_v2_{timestamp}.gif"
        animation_path = os.path.join('static/animations', animation_filename)
        
        if generate_animation_v2(particles, num_steps, delta, animation_path):
            # Salvar no banco de dados
            simulation = Simulation(
                version='v2',
                num_particles=num_particles,
                num_steps=num_steps,
                delta=delta,
                velocity_coefficient=velocity_coef,
                box_width=10.0,
                box_height=10.0,
                box_depth=10.0,
                animation_path=f'/static/animations/{animation_filename}',
                status='completed',
                execution_time=execution_time
            )
            db.session.add(simulation)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Simulação V2 concluída com sucesso',
                'animation_path': f'/static/animations/{animation_filename}',
                'execution_time': round(execution_time, 2),
                'simulation_id': simulation.id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao gerar animação'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na simulação V2: {str(e)}'
        }), 500

@app.route('/api/simulations', methods=['GET'])
def get_simulations():
    """Retorna lista de todas as simulações"""
    try:
        version = request.args.get('version')  # 'v1', 'v2' ou None para todas
        
        query = Simulation.query.order_by(Simulation.created_at.desc())
        
        if version:
            query = query.filter_by(version=version)
        
        simulations = query.all()
        
        return jsonify({
            'success': True,
            'data': [sim.to_dict() for sim in simulations]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar simulações: {str(e)}'
        }), 500

@app.route('/api/simulation/<int:sim_id>', methods=['GET'])
def get_simulation(sim_id):
    """Retorna detalhes de uma simulação específica"""
    try:
        simulation = Simulation.query.get_or_404(sim_id)
        return jsonify({
            'success': True,
            'data': simulation.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar simulação: {str(e)}'
        }), 500

@app.route('/api/simulation/<int:sim_id>', methods=['DELETE'])
def delete_simulation(sim_id):
    """Deleta uma simulação e sua animação"""
    try:
        simulation = Simulation.query.get_or_404(sim_id)
        
        # Deletar arquivo de animação se existir
        if simulation.animation_path:
            animation_file = simulation.animation_path.replace('/static/', '')
            full_path = os.path.join('static', animation_file)
            if os.path.exists(full_path):
                os.remove(full_path)
        
        db.session.delete(simulation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Simulação deletada com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar simulação: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Verificar saúde da aplicação"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
