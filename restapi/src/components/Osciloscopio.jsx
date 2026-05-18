import { useEffect, useRef } from 'react';

export default function Osciloscopio({ datos, color }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Configuración de estilo de línea
    ctx.lineWidth = 4;
    ctx.strokeStyle = color || '#34d399';
    ctx.shadowBlur = 10;
    ctx.shadowColor = color || '#34d399';
    ctx.lineJoin = 'round';
    
    const width = canvas.width;
    const height = canvas.height;
    const centerY = height / 2;

    ctx.beginPath();

    if (!datos || datos.length === 0) {
      // Línea base con ligero ruido si no hay datos
      ctx.moveTo(0, centerY);
      for (let x = 0; x < width; x += 5) {
        ctx.lineTo(x, centerY + (Math.random() - 0.5) * 4);
      }
    } else {
      const pasoX = width / (datos.length - 1);
      
      // El ESP32 manda valores de 0-4095 (12 bits). El centro es 2048.
      // Calculamos el valor relativo al centro para graficar.
      for (let i = 0; i < datos.length; i++) {
        const x = i * pasoX;
        
        // Normalizamos: (valor - offset) * escala
        // Usamos un factor de escala que haga que +/- 500 unidades llenen el canvas
        const valorRelativo = (datos[i] - 2048);
        const y = centerY - (valorRelativo * (height / 1500)); 

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    }

    ctx.stroke();

    // Dibujar cuadrícula de fondo (opcional, para estilo pro)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    ctx.shadowBlur = 0;
    for(let i=0; i<width; i+=50) {
      ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, height); ctx.stroke();
    }
    for(let i=0; i<height; i+=50) {
      ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(width, i); ctx.stroke();
    }

  }, [datos, color]);

  return (
    <div className='w-full h-full flex flex-col'>
      <div className='flex justify-between items-center mb-1 px-2'>
        <span className='text-[10px] font-mono text-slate-500 uppercase tracking-widest'>Señal de Entrada (12-bit ADC)</span>
        <span className='text-[10px] font-mono text-slate-500'>2500 Hz Sample Rate</span>
      </div>
      <div className='flex-1 bg-black/40 rounded-lg overflow-hidden border border-white/5 relative'>
        <canvas
          ref={canvasRef}
          width={1200}
          height={400}
          className="w-full h-full"
        />
      </div>
    </div>
  );
}
