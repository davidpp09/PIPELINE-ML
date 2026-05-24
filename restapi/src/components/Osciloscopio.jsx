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
    for (let i = 0; i < width; i += 50) {
      ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, height); ctx.stroke();
    }
    for (let i = 0; i < height; i += 50) {
      ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(width, i); ctx.stroke();
    }

    // Configuración de estilo de línea
    ctx.lineWidth = 3;
    ctx.strokeStyle = color || '#00ff41';
    ctx.shadowBlur = 8;
    ctx.shadowColor = color || '#00ff41';
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    ctx.beginPath();

    if (!datos || datos.length === 0) {
      ctx.moveTo(0, centerY);
      ctx.lineTo(width, centerY);
    } else {
      const pasoX = width / (datos.length - 1);

      // --- LÓGICA DE AUTO-ESCALA DINÁMICA ---
      // 1. Encontrar los límites reales de la señal entrante
      const minVal = Math.min(...datos);
      const maxVal = Math.max(...datos);
      let rango = maxVal - minVal;

      // 2. Si hay silencio (línea plana), forzamos un rango mínimo 
      // para evitar que amplifique el "ruido" microscópico.
      if (rango < 50) rango = 50;

      // 3. Crear márgenes (10% de padding arriba y abajo)
      const padding = height * 0.1;
      const altoEfectivo = height - (padding * 2);

      for (let i = 0; i < datos.length; i++) {
        const x = i * pasoX;

        // 4. Normalizar el valor de 0 a 1 respecto a sus propios límites
        const normalizado = (datos[i] - minVal) / rango;

        // 5. Mapear a la altura del Canvas (Invertimos porque Y=0 es arriba)
        const y = (height - padding) - (normalizado * altoEfectivo);

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
    }
    ctx.stroke();

  }, [datos, color]);

  return (
    <div className='w-full h-full flex flex-col'>
      <div className='flex justify-between items-center mb-1 px-2'>
        <span className='text-[10px] font-mono text-emerald-500/50 uppercase tracking-widest'>Osciloscopio Auto-Escala</span>
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