import { useEffect, useState, useRef } from 'react'
import PanelInstrumento from './components/PanelInstrumento'
import Osciloscopio from './components/Osiloscopio'
import Espectrograma from './components/Espectrograma'
import VistaMatematicas from './components/VistaMatematicas'

function App() {
  const [datos, setDatos] = useState({
    estado_sistema: "CONECTANDO...", instrumento: "ESPERANDO...", color: "#888888",
    senal_tiempo: new Array(100).fill(0), espectro_frecuencias: new Array(64).fill(0),
    metricas_dsp: { f0: 0, rms: 0, thd: 0, confianza: 0 },
    muestras_memoria: 0, ia_lista: false
  });

  const [vista, setVista] = useState('graficas');
  const wsRef = useRef(null); // Guardamos la conexión para poder usar el SEND

  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8080');
    wsRef.current.onmessage = (event) => {
      setDatos(prev => ({ ...prev, ...JSON.parse(event.data) }));
    };
    return () => wsRef.current?.close();
  }, []);

  // Función para darle órdenes al backend
  const enviarComando = (comandoObj) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(comandoObj));
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6 tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
        PIPELINE ML: DETECCIÓN ACÚSTICA
      </h1>

      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-3 gap-6">

        <div className="md:col-span-1">
          <PanelInstrumento
            datos={datos}
            enviarComando={enviarComando}
            vista={vista}
            setVista={setVista}
          />
        </div>

        <div className="md:col-span-2 flex flex-col gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 flex justify-between items-center shadow-md">
            <span className="text-emerald-400 font-mono text-sm tracking-widest px-4 font-bold animate-pulse">
              ESTADO: {datos.estado_sistema}
            </span>
            <span className="text-slate-500 font-mono text-xs px-4">
              DATASET: {datos.muestras_memoria} MUESTRAS | MODELO: {datos.ia_lista ? 'ENTRENADO' : 'NO ENTRENADO'}
            </span>
          </div>

          {vista === 'graficas' ? (
            <>
              <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 h-56">
                <Osciloscopio datos={datos.senal_tiempo} color={datos.color} />
              </div>
              <Espectrograma datosFrecuencia={datos.espectro_frecuencias} color={datos.color} />
            </>
          ) : (
            <VistaMatematicas instrumento={datos.instrumento} color={datos.color} metricas={datos.metricas_dsp} />
          )}
        </div>

      </div>
    </div>
  )
}
export default App