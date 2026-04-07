"use client";
import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import { Shield, AlertTriangle, Camera, Activity, User } from 'lucide-react';

// Connect to the Socket.io bridge server
const socket = io('http://localhost:4000');

interface SafetyData {
  score: number;
  status: string;
  label?: string;
}

export default function Home() {
  const [safetyData, setSafetyData] = useState<SafetyData>({ score: 100, status: "SAFE" });
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    socket.on('connect', () => setIsConnected(true));
    socket.on('disconnect', () => setIsConnected(false));

    socket.on('display_data', (data: SafetyData) => {
      setSafetyData(data);
    });

    return () => {
      socket.off('display_data');
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#0B2A41] text-white p-6 lg:p-10 font-sans selection:bg-[#47D6AD] selection:text-[#0B2A41]">
      {/* HEADER SECTION */}
      <header className="max-w-7xl mx-auto mb-10 border-b border-[#25A18E]/30 pb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-[#47D6AD]">
            MUFAKKER <span className="font-light text-white/70">SAFETY AI</span>
          </h1>
          <p className="text-xs uppercase tracking-[0.3em] text-[#25A18E] mt-1">Real-Time Protection System</p>
        </div>
        
        <div className="flex items-center gap-4 bg-[#004E64] px-4 py-2 rounded-full border border-[#25A18E]/20">
          <div className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isConnected ? 'bg-[#47D6AD]' : 'bg-red-500'}`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${isConnected ? 'bg-[#47D6AD]' : 'bg-red-500'}`}></span>
          </div>
          <span className="text-xs font-mono uppercase tracking-widest text-white/60">
            {isConnected ? 'System Live' : 'Reconnecting...'}
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* VIDEO FEED SECTION */}
        <div className="lg:col-span-2 relative group">
          <div className={`relative aspect-video bg-black rounded-3xl border-2 transition-all duration-500 overflow-hidden shadow-2xl flex items-center justify-center ${
            safetyData.status !== "SAFE" ? "border-red-500 shadow-red-500/20" : "border-[#25A18E]/40 shadow-[#25A18E]/10"
          }`}>
            <img 
              src="http://localhost:5000/video_feed" 
              alt="AI Detection Feed"
              className="w-full h-full object-contain"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
                e.currentTarget.nextElementSibling?.classList.remove('hidden');
              }}
            />
            {/* Fallback when video is off */}
            <div className="hidden absolute text-white/20 flex flex-col items-center gap-4">
              <Camera size={64} strokeWidth={1} className="animate-pulse" />
              <p className="text-sm font-mono tracking-tighter">WAITING FOR PYTHON STREAM (main.py)...</p>
            </div>
            
            {/* Feed Overlay Labels */}
            <div className="absolute top-4 left-4 flex gap-2">
              <span className="bg-black/60 backdrop-blur-md px-3 py-1 rounded-md text-[10px] font-bold border border-white/10 uppercase tracking-widest">YOLOv11n</span>
              <span className="bg-[#25A18E] px-3 py-1 rounded-md text-[10px] font-bold text-[#0B2A41] uppercase tracking-widest">Active</span>
            </div>
          </div>
        </div>

        {/* SIDEBAR ANALYTICS */}
        <div className="flex flex-col gap-6">
          {/* Compliance Score Card */}
          <div className="bg-[#004E64] p-8 rounded-3xl border border-[#25A18E]/30 shadow-xl relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-10 transition-opacity text-white">
              <Shield size={120} />
            </div>
            <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-[#47D6AD] mb-4">Compliance Score</h2>
            <div className="flex items-baseline gap-2">
              <span className="text-7xl font-black text-white leading-none">{safetyData.score}</span>
              <span className="text-2xl font-light text-[#25A18E]">%</span>
            </div>
            <div className="w-full bg-[#0B2A41] rounded-full h-2 mt-8 overflow-hidden border border-[#25A18E]/20">
              <div 
                className={`h-full transition-all duration-1000 ease-out ${safetyData.score > 80 ? 'bg-[#47D6AD]' : 'bg-red-500'}`} 
                style={{ width: `${safetyData.score}%` }}
              ></div>
            </div>
          </div>

          {/* Status Alert Card */}
          <div className={`p-8 rounded-3xl flex-1 flex flex-col items-center justify-center gap-4 border-2 transition-all duration-300 ${
            safetyData.status === "SAFE" 
            ? "bg-[#25A18E]/5 border-[#25A18E]/20 text-[#47D6AD]" 
            : "bg-red-500/10 border-red-500 text-red-500 animate-[pulse_1s_infinite]"
          }`}>
            {safetyData.status === "SAFE" ? (
              <Activity size={48} />
            ) : (
              <AlertTriangle size={48} />
            )}
            <p className="text-2xl font-black uppercase tracking-tighter">
              {safetyData.status === "SAFE" ? "System Secure" : "Safety Violation"}
            </p>
          </div>
          
          {/* Operator Profile Card */}
          <div className="bg-[#00364A] p-6 rounded-3xl border border-[#25A18E]/10 flex items-center justify-between group hover:border-[#25A18E]/40 transition-colors">
             <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#25A18E] rounded-2xl flex items-center justify-center text-[#0B2A41] group-hover:rotate-12 transition-transform shadow-lg">
                  <User size={24} />
                </div>
                <div>
                  <p className="text-[10px] uppercase font-bold text-white/40 tracking-widest">Active Operator</p>
                  <p className="text-lg font-bold text-white">Ziyad</p>
                </div>
             </div>
             <div className="text-[10px] font-mono text-[#47D6AD] bg-[#47D6AD]/10 px-2 py-1 rounded">ADMIN</div>
          </div>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-12 text-center">
        <p className="text-[10px] uppercase tracking-[0.5em] text-white/20">
          Developed by Mufakker Community &copy; 2026
        </p>
      </footer>
    </div>
  );
}