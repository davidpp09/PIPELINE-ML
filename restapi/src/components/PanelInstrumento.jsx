export default function PanelInstrumento({ instrumento, frecuencia }) {
  return (
    <div className='bg-slate-700 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-inner h-full'>
      <h2 className='text-sm uppercase tracking-widest text-slate-400 mb-4 font-semibold'>
        Instrumento Detectado
      </h2>
      <span className='text-4xl font-black text-emerald-400 drop-shadow-md transition-all mb-6'>
        {instrumento}
      </span>

      {/* Nuevo recuadro para el dato de la frecuencia */}
      <div className="bg-slate-800 w-full p-4 rounded-lg border border-slate-600">
        <h3 className="text-xs uppercase text-slate-500 mb-1 tracking-wider">Frecuencia Fundamental</h3>
        <span className="text-2xl font-bold text-sky-400">
          {frecuencia} <span className="text-sm text-slate-400 font-normal">Hz</span>
        </span>
      </div>
    </div>
  );
}
