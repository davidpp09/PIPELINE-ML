import { useState } from 'react';

export default function PanelInstrumento({ datos, enviarComando }) {
  const estaGrabando = datos.estado_sistema.includes("GRABANDO");
  const guardandoMuestra = datos.estado_sistema.startsWith("MUESTRA GUARDADA");

  // Instrumento seleccionado para grabar una nueva muestra de entrenamiento.
  const instrumentos = datos.instrumentos_validos || ["flauta", "guitarra", "teclado", "violin", "tambor"];
  const [etiqueta, setEtiqueta] = useState(instrumentos[0]);
  const conteo = datos.conteo_muestras || {};

  return (
    <div className='bg-slate-900 border border-slate-700 rounded-xl p-6 flex flex-col shadow-2xl h-full'>
      <div className="text-center mb-6 border-b border-slate-800 pb-6">
        <h2 className='text-[10px] uppercase tracking-widest text-slate-500 mb-2 font-bold font-mono text-emerald-400'>
          {estaGrabando ? 'Capturando Audio...' : 'Instrumento Detectado'}
        </h2>
        <span
          style={{
            color: estaGrabando ? '#f87171' : datos.color,
            textShadow: `0px 0px 20px ${estaGrabando ? '#f87171' : datos.color}80`
          }}
          className={`text-5xl font-black block transition-all ${estaGrabando ? 'animate-pulse' : ''}`}
        >
          {estaGrabando ? 'REC' : datos.instrumento.toUpperCase()}
        </span>
        {guardandoMuestra && (
          <span className="block mt-2 text-[10px] font-mono text-cyan-400 tracking-widest">
            ✓ Muestra añadida y modelo reentrenado
          </span>
        )}
      </div>

      <div className="flex-1 flex flex-col gap-4 justify-center">
        <button
          onClick={() => enviarComando({accion: 'detectar'})}
          disabled={estaGrabando}
          className={`w-full py-6 text-xl font-black rounded-xl tracking-widest transition-all shadow-[0_0_20px_rgba(16,185,129,0.4)] active:scale-95 ${
            estaGrabando
            ? 'bg-slate-800 text-slate-600 cursor-not-allowed border border-slate-700'
            : 'bg-emerald-500 hover:bg-emerald-400 text-black'
          }`}
        >
          {estaGrabando ? 'ESCUCHANDO...' : '🎤 ESCUCHAR (5s)'}
        </button>

        <button
          onClick={() => enviarComando({accion: 'detener'})}
          className="w-full py-3 text-slate-500 hover:text-red-400 transition-colors font-mono text-sm border border-slate-800 rounded-lg hover:border-red-900/30"
        >
          ⏹ DETENER / RESET
        </button>
      </div>

      {/* --- Entrenamiento: grabar muestras para mejorar la detección --- */}
      <div className="mt-6 pt-6 border-t border-slate-800">
        <h3 className="text-[10px] uppercase tracking-widest text-slate-500 mb-3 font-bold font-mono">
          🧠 Entrenar (grabar muestra)
        </h3>
        <div className="flex gap-2">
          <select
            value={etiqueta}
            onChange={(e) => setEtiqueta(e.target.value)}
            disabled={estaGrabando}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-cyan-500 disabled:opacity-50"
          >
            {instrumentos.map((inst) => (
              <option key={inst} value={inst}>
                {inst} ({conteo[inst] || 0})
              </option>
            ))}
          </select>
          <button
            onClick={() => enviarComando({ accion: 'grabar_muestra', etiqueta })}
            disabled={estaGrabando}
            className={`px-4 py-2 text-sm font-bold rounded-lg tracking-wide transition-all active:scale-95 ${
              estaGrabando
              ? 'bg-slate-800 text-slate-600 cursor-not-allowed border border-slate-700'
              : 'bg-cyan-600 hover:bg-cyan-500 text-white'
            }`}
          >
            ● GRABAR
          </button>
        </div>
        <p className="text-[9px] font-mono text-slate-600 mt-2 leading-tight">
          Toca el instrumento durante 5 s. La muestra se guarda y el modelo se reentrena al instante.
        </p>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-800">
        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <span>IA STATUS: {datos.ia_lista ? 'MODELO CARGADO' : 'SIN MODELO'}</span>
          <span>MUESTRAS: {datos.muestras_memoria || 0}</span>
        </div>
      </div>
    </div>
  );
}
