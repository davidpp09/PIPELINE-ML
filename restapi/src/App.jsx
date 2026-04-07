import { useEffect, useState, useRef } from 'react'
import PanelInstrumento from './components/PanelInstrumento'
import Osciloscopio from './components/Osiloscopio'
import Espectrograma from './components/Espectrograma'
import VistaMatematicas from './components/VistaMatematicas'
import './index.css'

function App() {
  const [datos, setDatos] = useState({
    instrumento: "ESPERANDO...",
    color: "#888888",
    senal_tiempo: new Array(100).fill(0),
    espectro_frecuencias: new Array(64).fill(0),
    metricas_dsp: { f0: 0, rms: 0, thd: 0, confianza: 0 } // <- ESTO ES NUEVO
  });

  const [pausado, setPausado] = useState(false);
  const [vista, setVista] = useState('graficas'); // 'graficas' o 'matematicas'

  // Usamos useRef para acceder al valor actual de 'pausado' dentro del WebSocket
  const pausadoRef = useRef(pausado);
  useEffect(() => {
    pausadoRef.current = pausado;
  }, [pausado]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080');

    ws.onmessage = (event) => {
      if (!pausadoRef.current) {
        const dataRecibida = JSON.parse(event.data);

        // Usamos prevDatos para conservar las llaves originales (como metricas_dsp)
        // y solo sobrescribir las que sí vienen en dataRecibida.
        setDatos(prevDatos => ({
          ...prevDatos,
          ...dataRecibida
        }));
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-8 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-8 tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        DETECTOR DE INSTRUMENTOS IA
      </h1>

      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6">

        <div className="md:col-span-1">
          <PanelInstrumento
            instrumento={datos.instrumento}
            color={datos.color}
            pausado={pausado}
            setPausado={setPausado}
            vista={vista}
            setVista={setVista}
          />
        </div>

        <div className="md:col-span-2 flex flex-col gap-4">
          {/* Lógica de pestañas: mostramos gráficas o matemáticas */}
          {vista === 'graficas' ? (
            <>
              <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 h-48">
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