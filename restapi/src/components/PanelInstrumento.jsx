export default function PanelInstrumento({ instrumento, color, pausado, setPausado, vista, setVista }) {

  let descripcion = "Esperando señal de entrada...";
  if (instrumento === "GUITARRA") descripcion = "Detección basada en armónicos múltiples. Se observan picos claros por encima de la fundamental.";
  else if (instrumento === "FLAUTA") descripcion = "Señal con alta pureza espectral. La energía se concentra casi en una sola frecuencia.";
  else if (instrumento === "TECLADO") descripcion = "Contenido armónico denso y constante. Frecuencias sostenidas (sustain) características.";

  return (
    <div className='bg-slate-900 border border-slate-700 rounded-xl p-6 flex flex-col items-center justify-center text-center shadow-2xl h-full'>

      <h2 className='text-xs uppercase tracking-widest text-slate-400 mb-2 font-bold font-mono'>
        RESULTADO DE IA
      </h2>

      <span
        style={{ color: color || '#34d399', textShadow: `0px 0px 15px ${color || '#34d399'}80` }}
        className='text-5xl font-black transition-all mb-8'
      >
        {instrumento}
      </span>

      <div className="bg-black w-full p-4 rounded-lg border border-slate-800 shadow-inner mb-6">
        <h3 className="text-[10px] uppercase text-slate-500 mb-2 tracking-widest font-mono">
          Análisis de la Señal
        </h3>
        <p className="text-sm text-slate-300 font-light italic">
          {descripcion}
        </p>
      </div>

      {/* NUEVOS BOTONES DE CONTROL */}
      <div className="flex flex-col w-full gap-3 mt-auto">
        <button
          onClick={() => setPausado(!pausado)}
          className={`w-full py-3 rounded-lg font-bold text-sm tracking-wider transition-all duration-300 ${pausado
              ? 'bg-red-500/20 text-red-400 border border-red-500 hover:bg-red-500/40'
              : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500 hover:bg-emerald-500/40'
            }`}
        >
          {pausado ? "▶ REANUDAR ESCUCHA" : "⏸ DETENER ESCUCHA"}
        </button>

        <button
          onClick={() => setVista(vista === 'graficas' ? 'matematicas' : 'graficas')}
          className="w-full py-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 rounded-lg font-bold text-sm tracking-wider transition-all"
        >
          {vista === 'graficas' ? "📚 VER MATEMÁTICAS" : "📊 VOLVER A GRÁFICAS"}
        </button>
      </div>

    </div>
  );
}