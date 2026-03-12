import { useState, useEffect } from 'react';
import Header from './components/Header';
import PanelInstrumento from './components/PanelInstrumento';
import Osciloscopio from './components/Osiloscopio';

function App() {
  // 1. Estados globales (Ahora incluimos la onda y la frecuencia)
  const [estadoConexion, setEstadoConexion] = useState('Buscando servidor...');
  const [instrumento, setInstrumento] = useState('--');
  const [frecuencia, setFrecuencia] = useState(0);
  const [datosOnda, setDatosOnda] = useState([]);

  // 2. Conexión WebSocket real a Python
  useEffect(() => {
    // Nos conectamos al puerto 8080 que definimos e Python
    const socket = new WebSocket('https://silver-couscous-v6pqpxxgqxq9cx7wg-8080.app.github.dev/');

    socket.onopen = () => {
      console.log('¡Conectado al backend de Python!');
      setEstadoConexion('EN LINEA');
    };

    // Esto se dispara unas 20-30 veces por segundo cuando Python habla
    socket.onmessage = (evento) => {
      try {
        const datos = JSON.parse(evento.data);
        
        // Actualizamos la interfaz con los datos del contrato
        if (datos.instrumento) setInstrumento(datos.instrumento);
        if (datos.frecuencia_hz !== undefined) setFrecuencia(datos.frecuencia_hz);
        if (datos.senal_tiempo) setDatosOnda(datos.senal_tiempo);
        
      } catch (error) {
        console.error("Error leyendo a Python:", error);
      }
    };

    socket.onclose = () => {
      setEstadoConexion('Desconectado');
    };

    // Limpieza al cerrar la pestaña
    return () => socket.close();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8 flex flex-col">
      <Header estadoConexion={estadoConexion} />

      <div className='grid grid-cols-3 gap-6 w-full max-w-7xl mx-auto mt-8 bg-slate-800 p-5 flex-1 rounded-xl shadow-lg'>
        {/* Le pasamos el arreglo de números reales al osciloscopio */}
        <Osciloscopio estadoConexion={estadoConexion} datosOnda={datosOnda} />
        
        {/* Le pasamos el instrumento y la frecuencia al panel */}
        <PanelInstrumento instrumento={instrumento} frecuencia={frecuencia} />
      </div>
    </div>
  );
}

export default App;
