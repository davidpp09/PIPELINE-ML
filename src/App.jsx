// =============================================================================
// COMPONENTE RAÍZ DEL FRONTEND
// -----------------------------------------------------------------------------
// Se conecta al backend por WebSocket y recibe ~25 paquetes JSON por segundo
// con: la señal en el tiempo, el espectro de frecuencias, las métricas DSP
// (f0, RMS, THD) y el estado del sistema. Reparte esos datos a 3 componentes:
//   - PanelInstrumento: botones de control y resultado de la detección
//   - Osciloscopio: la señal en el dominio del TIEMPO
//   - Espectrograma: la huella en el dominio de la FRECUENCIA
// =============================================================================
import { useEffect, useState, useRef } from 'react'
import PanelInstrumento from './components/PanelInstrumento'
import Osciloscopio from './components/Osciloscopio'
import Espectrograma from './components/Espectrograma'

function App() {
  // Estado con el último paquete recibido del backend.
  // Estos valores iniciales son "placeholders" mientras conecta.
  const [datos, setDatos] = useState({
    estado_sistema: "CONECTANDO...", instrumento: "ESPERANDO...", color: "#888888",
    senal_tiempo: new Array(100).fill(2048), espectro_frecuencias: new Array(64).fill(0),
    metricas_dsp: { f0: 0, rms: 0, thd: 0, confianza: 0 },
    muestras_memoria: 0, ia_lista: false
  });

  // "Congelado" = cuando llega un resultado, dejamos de actualizar la pantalla
  // para que el usuario vea la señal del sonido grabado (y no el silencio de después).
  const [congelado, setCongelado] = useState(false);
  const wsRef = useRef(null);
  // Ref para leer el estado de "congelado" dentro del onmessage sin re-suscribir
  const congeladoRef = useRef(false);

  useEffect(() => {
    // URL del backend local del usuario. Se puede sobreescribir con la
    // variable de entorno VITE_WS_URL al hacer el build (ver .env.example).
    const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8081';
    wsRef.current = new WebSocket(WS_URL);
    wsRef.current.onmessage = (event) => {
      // Si la pantalla está congelada, ignoramos los datos en vivo
      if (congeladoRef.current) return;

      const nuevo = JSON.parse(event.data);
      setDatos(prev => ({ ...prev, ...nuevo }));

      // Al llegar el resultado, congelamos la pantalla con la señal y huella detectadas
      if (nuevo.estado_sistema === "RESULTADO LISTO") {
        congeladoRef.current = true;
        setCongelado(true);
      }
    };
    return () => wsRef.current?.close();
  }, []);

  // Manda un comando JSON al backend, ej. {accion:'detectar'} o
  // {accion:'grabar_muestra', etiqueta:'guitarra'}. Lo usan los botones del panel.
  const enviarComando = (comandoObj) => {
    // Cualquier acción (escuchar de nuevo o detener) descongela la pantalla
    if (comandoObj.accion === 'detectar' || comandoObj.accion === 'detener') {
      congeladoRef.current = false;
      setCongelado(false);
    }
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
            <span className={`font-mono text-xs tracking-widest px-4 font-bold ${congelado ? 'text-cyan-400' : 'text-emerald-400 animate-pulse'}`}>
              {datos.estado_sistema}
            </span>
            {congelado && (
              <span className="text-[10px] font-mono text-cyan-400 border border-cyan-500/40 rounded px-2 py-1 mr-2 tracking-widest">
                ❄ CONGELADO
              </span>
            )}
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
