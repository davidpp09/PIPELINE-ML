export default function PanelInstrumento({ datos, enviarComando, vista, setVista }) {
  
  return (
    <div className='bg-slate-900 border border-slate-700 rounded-xl p-6 flex flex-col shadow-2xl h-full'>
      
      <div className="text-center mb-6 border-b border-slate-800 pb-6">
        <h2 className='text-[10px] uppercase tracking-widest text-slate-500 mb-2 font-bold font-mono'>PREDICCIÓN ACTUAL</h2>
        <span style={{ color: datos.color, textShadow: `0px 0px 15px ${datos.color}80` }} className='text-4xl font-black block transition-all'>
          {datos.instrumento}
        </span>
      </div>

      {/* CONTROLES DE MACHINE LEARNING */}
      <div className="flex-1 flex flex-col gap-4">
        
        <div className="bg-black/50 p-4 rounded-lg border border-slate-800">
          <h3 className="text-xs text-slate-400 mb-3 font-bold tracking-widest">1. CONSTRUIR DATASET</h3>
          <div className="grid grid-cols-2 gap-2">
            <button onClick={() => enviarComando({accion: 'grabar_datos', instrumento: 'flauta'})} className="bg-slate-800 hover:bg-emerald-900/50 text-xs py-2 rounded text-slate-300 border border-slate-700 hover:border-emerald-500 transition-all">🎤 Grabar Flauta</button>
            <button onClick={() => enviarComando({accion: 'grabar_datos', instrumento: 'guitarra'})} className="bg-slate-800 hover:bg-red-900/50 text-xs py-2 rounded text-slate-300 border border-slate-700 hover:border-red-500 transition-all">🎤 Grabar Guitarra</button>
            <button onClick={() => enviarComando({accion: 'grabar_datos', instrumento: 'teclado'})} className="bg-slate-800 hover:bg-blue-900/50 text-xs py-2 rounded text-slate-300 border border-slate-700 hover:border-blue-500 transition-all">🎤 Grabar Teclado</button>
          </div>
        </div>

        <div className="bg-black/50 p-4 rounded-lg border border-slate-800">
          <h3 className="text-xs text-slate-400 mb-3 font-bold tracking-widest">2. ENTRENAR MODELO</h3>
          <button 
            onClick={() => enviarComando({accion: 'entrenar_modelo'})}
            disabled={datos.muestras_memoria < 10}
            className={`w-full py-2 text-sm font-bold rounded tracking-widest transition-all ${datos.muestras_memoria >= 10 ? 'bg-purple-600 hover:bg-purple-500 text-white' : 'bg-slate-800 text-slate-600 cursor-not-allowed'}`}
          >
            ⚙️ EJECUTAR RANDOM FOREST
          </button>
        </div>

        <div className="bg-black/50 p-4 rounded-lg border border-slate-800 mt-auto">
          <h3 className="text-xs text-slate-400 mb-3 font-bold tracking-widest">3. PRODUCCIÓN (INFERENCIA)</h3>
          <button 
            onClick={() => enviarComando({accion: 'detectar'})}
            disabled={!datos.ia_lista}
            className={`w-full py-3 text-sm font-black rounded tracking-widest transition-all ${datos.ia_lista ? 'bg-emerald-500 hover:bg-emerald-400 text-black shadow-[0_0_15px_rgba(16,185,129,0.5)]' : 'bg-slate-800 text-slate-600 cursor-not-allowed'}`}
          >
            🎯 INICIAR DETECCIÓN
          </button>
          
          <button onClick={() => enviarComando({accion: 'detener'})} className="w-full mt-2 text-xs py-2 text-slate-500 hover:text-red-400 transition-colors">
            ⏹ Detener / Resetear Estado
          </button>
        </div>

      </div>

      <button onClick={() => setVista(vista === 'graficas' ? 'matematicas' : 'graficas')} className="w-full mt-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 rounded-lg font-bold text-xs tracking-wider transition-all">
        {vista === 'graficas' ? "📚 VER MATEMÁTICAS DSP" : "📊 VOLVER A GRÁFICAS"}
      </button>

    </div>
  );
}