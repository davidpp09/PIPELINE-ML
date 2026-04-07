import { useEffect, useRef } from 'react';

// Ahora recibimos 'datos' y 'color' para que coincida exactamente con App.jsx
export default function Osciloscopio({ datos, color }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Borramos el frame anterior
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 3;
    // Usamos el color dinámico que viene de Python (Verde, Rojo, Azul o Amarillo)
    ctx.strokeStyle = color || '#34d399';
    ctx.shadowBlur = 15;
    ctx.shadowColor = color || '#34d399';
    ctx.beginPath();

    const centroY = canvas.height / 2;

    // Si no hay datos, dibujamos el ruido base
    if (!datos || datos.length === 0) {
      for (let x = 0; x < canvas.width; x++) {
        let y = centroY + (Math.random() - 0.5) * 5;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    } else {
      // DIBUJAR LA ONDA REAL DE PYTHON
      const pasoX = canvas.width / datos.length;

      for (let i = 0; i < datos.length; i++) {
        const x = i * pasoX;
        // Multiplicamos para amplificar la señal visualmente
        const y = centroY - (datos[i] * 100);

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    }

    ctx.stroke();

    // Se vuelve a ejecutar cuando llega una onda nueva o cambia el color
  }, [datos, color]);

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