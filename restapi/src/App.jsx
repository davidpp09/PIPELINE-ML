import { useEffect, useState, useRef } from 'react'
import PanelInstrumento from './components/PanelInstrumento'
import Osciloscopio from './components/Osciloscopio'
import Espectrograma from './components/Espectrograma'

function App() {
  const [datos, setDatos] = useState({
    estado_sistema: "CONECTANDO...", instrumento: "ESPERANDO...", color: "#888888",
    senal_tiempo: new Array(100).fill(2048), espectro_frecuencias: new Array(64).fill(0),
    metricas_dsp: { f0: 0, rms: 0, thd: 0, confianza: 0 },
    muestras_memoria: 0, ia_lista: false
  });

  const wsRef = useRef(null);

  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8081');
    wsRef.current.onmessage = (event) => {
      setDatos(prev => ({ ...prev, ...JSON.parse(event.data) }));
    };
    return () => wsRef.current?.close();
  }, []);

  const enviarComando = (comandoObj) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(comandoObj));
    }
  };

  return (
    <div className="h-screen text-white p-6 flex flex-col items-center relative overflow-hidden bg-slate-950">
      <div className="tech-overlay"></div>

      <h1 className="text-3xl font-mono font-bold mb-4 tracking-tighter text-emerald-500 matrix-glow relative z-10">
        SISTEMA DE DETECCIÓN ACÚSTICA
      </h1>

      <div className="w-full max-w-7xl grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10 flex-1 overflow-hidden">

        {/* Panel Izquierdo: Control y Resultado */}
        <div className="md:col-span-1 h-full">
          <PanelInstrumento
            datos={datos}
            enviarComando={enviarComando}
          />
        </div>

        {/* Panel Derecho: Visualización */}
        <div className="md:col-span-2 flex flex-col gap-4 h-full overflow-hidden">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-2 flex justify-between items-center shadow-md shrink-0">
            <span className="text-emerald-400 font-mono text-xs tracking-widest px-4 font-bold animate-pulse">
              {datos.estado_sistema}
            </span>
          </div>

          {/* Osciloscopio - Altura flexible pero contenida */}
          <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 flex-1 min-h-0 shadow-inner">
            <Osciloscopio datos={datos.senal_tiempo} color={datos.color} />
          </div>

          {/* Espectrograma - Altura flexible pero contenida */}
          <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 flex-1 min-h-0 shadow-inner">
            <Espectrograma datosFrecuencia={datos.espectro_frecuencias} color={datos.color} />
          </div>
        </div>

      </div>
    </div>
  )
}
export default App
