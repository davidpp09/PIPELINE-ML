import { useEffect, useRef } from 'react';

export default function Osciloscopio({ datos, color }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const width = canvas.width;
    const height = canvas.height;
    const centerY = height / 2;

    // Limpiar canvas totalmente
    ctx.clearRect(0, 0, width, height);
    
    // Dibujar cuadrícula de fondo tenue
    ctx.strokeStyle = 'rgba(0, 255, 65, 0.1)';
    ctx.lineWidth = 1;
    for(let i=0; i<width; i+=50) {
      ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, height); ctx.stroke();
    }
    for(let i=0; i<height; i+=50) {
      ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(width, i); ctx.stroke();
    }

    // Configuración de estilo de línea (más gruesa y brillante)
    ctx.lineWidth = 3;
    ctx.strokeStyle = color || '#00ff41';
    ctx.shadowBlur = 8;
    ctx.shadowColor = color || '#00ff41';
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    
    ctx.beginPath();

    if (!datos || datos.length === 0) {
      // Línea base central si no hay datos
      ctx.moveTo(0, centerY);
      ctx.lineTo(width, centerY);
    } else {
      const pasoX = width / (datos.length - 1);
      
      for (let i = 0; i < datos.length; i++) {
        const x = i * pasoX;
        // Normalización: El ESP32 manda 0-4095. 
        // Aplicamos un zoom vertical para que pequeñas variaciones se vean.
        const valorRelativo = (datos[i] - 2048);
        // Factor de escala: height / 1000 hace que +/- 500 llene el canvas
        const y = centerY - (valorRelativo * (height / 1200)); 

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    }
    ctx.stroke();

  }, [datos, color]);

  return (
    <div className='w-full h-full flex flex-col'>
      <div className='flex justify-between items-center mb-1 px-2'>
        <span className='text-[10px] font-mono text-emerald-500/50 uppercase tracking-widest'>Osciloscopio Real-Time (ADC 12-bit)</span>
        <span className='text-[10px] font-mono text-slate-500'>{datos?.length || 0} muestras</span>
      </div>
      <div className='flex-1 bg-slate-950 rounded-lg overflow-hidden border border-emerald-500/20 shadow-inner'>
        <canvas
          ref={canvasRef}
          width={800}
          height={300}
          className="w-full h-full block"
        />
      </div>
    </div>
  );
}
