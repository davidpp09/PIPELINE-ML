export default function Header({estadoConexion}){
    const colorFondo = estadoConexion ==='EN LINEA' ? 'bg-green-400 text-slate-900'  : 'bg-yellow-400 text-slate-900';
    return(
   <header className="flex justify-between gap-5 w-full text-center mx-auto items-center">
        <h1 className="text-3xl font-bold ">Analizador de Señales</h1>
        <p className={`px-4 py-2 ${colorFondo} rounded-xl font-bold shadow-sm transition-colors duration-300`}>
          {estadoConexion}
        </p>
      </header>
    );
 
}