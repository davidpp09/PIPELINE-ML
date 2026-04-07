import React from 'react';

export default function VistaMatematicas({ instrumento, color, metricas }) {
    let titulo = "Esperando Detección...";
    let formula = "x(t) = 0";

    if (instrumento === "FLAUTA") {
        titulo = "Onda Senoidal Pura";
        formula = "x(t) = A * sin(2π * f0 * t)";
    } else if (instrumento === "GUITARRA") {
        titulo = "Serie Armónica Compleja";
        formula = "x(t) = Σ [An * sin(2π * n * f0 * t)]";
    } else if (instrumento === "TECLADO") {
        titulo = "Síntesis de Onda";
        formula = "x(t) = (4A/π) * Σ [sin(2π * (2k-1) * f0 * t) / (2k-1)]";
    }

    // Componente interno para las "tarjetas" de métricas
    const MetricaCard = ({ label, valor, unidad }) => (
        <div className="bg-black border border-slate-700 rounded-lg p-4 flex flex-col items-center justify-center shadow-inner">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">{label}</span>
            <div className="text-2xl font-black" style={{ color: color || '#34d399' }}>
                {valor} <span className="text-sm font-light text-slate-400">{unidad}</span>
            </div>
        </div>
    );

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-8 flex flex-col justify-between h-full shadow-2xl">
            <div>
                <h2 className="text-xl font-bold text-slate-300 mb-6 uppercase tracking-wider">
                    Análisis Cuantitativo (DSP)
                </h2>

                <h3 style={{ color: color || '#34d399' }} className="text-2xl font-black mb-4">
                    {titulo}
                </h3>

                <div className="bg-black border border-slate-800 rounded-lg p-4 mb-8 flex justify-center items-center shadow-inner">
                    <code className="text-emerald-400 text-lg font-mono tracking-widest">
                        {formula}
                    </code>
                </div>
            </div>

            {/* Rejilla de Métricas en Tiempo Real */}
            <div className="grid grid-cols-2 gap-4">
                <MetricaCard label="Pico Fundamental (f0)" valor={metricas?.f0 || 0} unidad="Hz" />
                <MetricaCard label="Potencia RMS" valor={metricas?.rms || 0} unidad="V" />
                <MetricaCard label="Índice THD" valor={metricas?.thd || 0} unidad="" />
                <MetricaCard label="Certeza del Modelo IA" valor={metricas?.confianza || 0} unidad="%" />
            </div>
        </div>
    );
}