export default function PanelInstrumento({ datos, enviarComando }) {
  return (
    <div className='bg-slate-900 border border-slate-700 rounded-xl p-6 flex flex-col shadow-2xl h-full'>
      <div className="text-center mb-6 border-b border-slate-800 pb-6">
        <h2 className='text-[10px] uppercase tracking-widest text-slate-500 mb-2 font-bold font-mono text-emerald-400'>
          Instrumento Detectado
        </h2>
        <span style={{ color: datos.color, textShadow: `0px 0px 20px ${datos.color}80` }} className='text-5xl font-black block transition-all'>
          {datos.instrumento.toUpperCase()}
        </span>
      </div>

      <div className="flex-1 flex flex-col gap-4 justify-center">
        <button 
          onClick={() => enviarComando({accion: 'detectar'})}
          className="w-full py-6 text-xl font-black rounded-xl tracking-widest transition-all bg-emerald-500 hover:bg-emerald-400 text-black shadow-[0_0_20px_rgba(16,185,129,0.4)] active:scale-95"
        >
          🎤 ESCUCHAR
        </button>
        
        <button 
          onClick={() => enviarComando({accion: 'detener'})} 
          className="w-full py-3 text-slate-500 hover:text-red-400 transition-colors font-mono text-sm border border-slate-800 rounded-lg hover:border-red-900/30"
        >
          ⏹ DETENER
        </button>
      </div>

      <div className="mt-6 pt-6 border-t border-slate-800">
        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <span>IA STATUS: {datos.ia_lista ? 'OPTIMIZED' : 'READY'}</span>
          <span>CONF: {datos.metricas_dsp.confianza.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
}
