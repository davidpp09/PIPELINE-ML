import { useEffect, useRef } from 'react';

// Ahora recibimos datosOnda en lugar de instrumento
export default function Osciloscopio({ estadoConexion, datosOnda }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Borramos el frame anterior
    ctx.clearRect(0, 0, canvas.width, canvas.height); 
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#34d399'; 
    ctx.shadowBlur = 15;         
    ctx.shadowColor = '#34d399'; 
    ctx.beginPath();

    const centroY = canvas.height / 2;

    if (estadoConexion !== 'EN LINEA' || datosOnda.length === 0) {
      // Línea plana con un poco de ruido si está desconectado
      for (let x = 0; x < canvas.width; x++) {
        let y = centroY + (Math.random() - 0.5) * 5;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    } else {
      // DIBUJAR LA ONDA REAL DE PYTHON
      const pasoX = canvas.width / datosOnda.length;

      for (let i = 0; i < datosOnda.length; i++) {
        const x = i * pasoX;
        // Multiplicamos por 100 para amplificar la señal visualmente en la pantalla
        const y = centroY - (datosOnda[i] * 100); 

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    }

    ctx.stroke(); 

  // Este useEffect se vuelve a ejecutar solo cuando Python manda un nuevo datosOnda
  }, [estadoConexion, datosOnda]);

  return (
    <div className='col-span-2 bg-slate-900 border border-slate-700 rounded-xl p-4 flex flex-col h-full'>
      <h2 className='text-xl mb-4 font-bold text-slate-300 text-center'>Osciloscopio en Tiempo Real</h2>
      <div className='w-full bg-black rounded-xl flex justify-center items-center flex-1 overflow-hidden relative border border-slate-800 shadow-inner'> 
        <canvas 
          ref={canvasRef} 
          width={800} 
          height={300} 
          className="w-full h-full object-cover"
        />
      </div>
    </div>
  );
}
