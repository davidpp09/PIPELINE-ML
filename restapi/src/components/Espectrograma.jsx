import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const Espectrograma = ({ datosFrecuencia, color }) => {
    // Transformación de datos para Recharts [cite: 2026-03-01]
    const data = datosFrecuencia.map((v, i) => ({ hz: i * 15, power: v }));

    return (
        <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 shadow-2xl">
            <h3 className="text-gray-400 text-xs font-mono mb-4 tracking-tighter">
                ANÁLISIS DE FRECUENCIA (HUELLA DIGITAL)
            </h3>
            <div style={{ width: '100%', height: 250 }}> {/* Altura fija para evitar el error */}
                <ResponsiveContainer>
                    <BarChart data={data}>
                        <XAxis dataKey="hz" hide />
                        <YAxis hide domain={[0, 1]} />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#111', border: 'none' }}
                            itemStyle={{ color: color }}
                        />
                        <Bar dataKey="power" fill={color} isAnimationActive={false} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default Espectrograma;