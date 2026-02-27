import { useState, useEffect, useCallback, useRef } from "react";
import "@/App.css";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Target, Database, FileCode, Archive, Cpu, 
  Plus, Trash2, Edit, Save, X, RefreshCw,
  Send, ChevronRight, Download, Zap, Shield,
  Crosshair, Activity, Settings, Menu, Copy,
  Loader2, AlertCircle, Check, Star, Eye
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============== API FUNCTIONS ==============
const api = {
  // Weapons
  getWeapons: () => axios.get(`${API}/weapons`),
  createWeapon: (data) => axios.post(`${API}/weapons`, data),
  updateWeapon: (id, data) => axios.put(`${API}/weapons/${id}`, data),
  deleteWeapon: (id) => axios.delete(`${API}/weapons/${id}`),
  seedWeapons: () => axios.post(`${API}/seed-weapons`),
  
  // Scripts
  getScripts: () => axios.get(`${API}/scripts`),
  createScript: (data) => axios.post(`${API}/scripts`, data),
  deleteScript: (id) => axios.delete(`${API}/scripts/${id}`),
  generateMasterScript: () => axios.post(`${API}/generate-master-script`),
  
  // Chat
  sendMessage: (sessionId, message) => axios.post(`${API}/chat`, { session_id: sessionId, message }),
  getChatHistory: (sessionId) => axios.get(`${API}/chat/${sessionId}`),
  clearChat: (sessionId) => axios.delete(`${API}/chat/${sessionId}`),
  
  // Stats
  getStats: () => axios.get(`${API}/stats`),
};

// ============== SIDEBAR COMPONENT ==============
function Sidebar({ activeTab, setActiveTab, stats }) {
  const navItems = [
    { id: 'dashboard', icon: Activity, label: 'DASHBOARD' },
    { id: 'meta', icon: Database, label: 'META CENTER' },
    { id: 'ai', icon: Target, label: 'IA EXPERTE' },
    { id: 'scripts', icon: Archive, label: 'COFFRE-FORT' },
  ];

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/20 border border-primary/50 flex items-center justify-center">
            <Crosshair className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="font-heading text-lg font-bold text-primary text-glow tracking-wider">ZEN HUB</h1>
            <p className="text-[10px] font-mono text-muted-foreground tracking-widest">PRO v1.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <button
            key={item.id}
            data-testid={`nav-${item.id}`}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 font-mono text-xs uppercase tracking-wider transition-all border ${
              activeTab === item.id
                ? 'bg-primary/10 border-primary/50 text-primary'
                : 'border-transparent hover:bg-secondary hover:border-border text-muted-foreground hover:text-foreground'
            }`}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </button>
        ))}
      </nav>

      {/* Stats Footer */}
      <div className="p-4 border-t border-border space-y-3">
        <div className="flex justify-between items-center text-[10px] font-mono">
          <span className="text-muted-foreground">ARMES</span>
          <span className="text-primary">{stats.total_weapons || 0}</span>
        </div>
        <div className="flex justify-between items-center text-[10px] font-mono">
          <span className="text-muted-foreground">SCRIPTS</span>
          <span className="text-accent">{stats.total_scripts || 0}</span>
        </div>
        <div className="flex justify-between items-center text-[10px] font-mono">
          <span className="text-muted-foreground">MÉTA</span>
          <span className="text-primary">{stats.meta_weapons || 0}</span>
        </div>
        <div className="h-1 bg-secondary overflow-hidden">
          <div className="h-full bg-primary pulse-glow" style={{ width: '100%' }}></div>
        </div>
        <p className="text-[9px] text-muted-foreground font-mono text-center">SYSTÈME OPÉRATIONNEL</p>
      </div>
    </aside>
  );
}

// ============== DASHBOARD COMPONENT ==============
function Dashboard({ stats, onNavigate, onGenerateMaster }) {
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await onGenerateMaster();
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-heading text-3xl font-bold text-primary text-glow tracking-wider">CENTRE DE COMMANDE</h2>
          <p className="text-sm text-muted-foreground font-mono mt-1">SYSTÈME DE GÉNÉRATION DE SCRIPTS WARZONE</p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="w-2 h-2 bg-primary rounded-full pulse-glow"></div>
          <span className="text-primary">EN LIGNE</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          icon={Database} 
          label="ARMES TOTALES" 
          value={stats.total_weapons || 0} 
          color="primary"
          onClick={() => onNavigate('meta')}
        />
        <StatCard 
          icon={Star} 
          label="MÉTA ACTUEL" 
          value={stats.meta_weapons || 0} 
          color="accent"
          onClick={() => onNavigate('meta')}
        />
        <StatCard 
          icon={Eye} 
          label="MÉTA CACHÉ" 
          value={stats.hidden_meta_weapons || 0} 
          color="destructive"
          onClick={() => onNavigate('meta')}
        />
        <StatCard 
          icon={FileCode} 
          label="SCRIPTS SAUVÉS" 
          value={stats.total_scripts || 0} 
          color="primary"
          onClick={() => onNavigate('scripts')}
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Master Script Generator */}
        <div className="bg-card border border-border p-6 corner-brackets">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-primary/20 border border-primary/50 flex items-center justify-center">
              <Cpu className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="font-heading text-lg font-bold">MASTER ENGINE</h3>
              <p className="text-[10px] text-muted-foreground font-mono">COMPILATEUR GPC v3.0</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Compile toutes les armes de votre base de données en un seul script GPC avec auto-détection ADT.
          </p>
          <div className="space-y-2 mb-4 text-[10px] font-mono">
            <div className="flex justify-between">
              <span className="text-muted-foreground">AUTO-DETECTION ADT</span>
              <span className="text-primary">ACTIVÉ</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">SUPPORT OLED</span>
              <span className="text-primary">v2.1</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">PROFILS WEAPON</span>
              <span className="text-accent">{stats.total_weapons || 0}</span>
            </div>
          </div>
          <button
            data-testid="generate-master-btn"
            onClick={handleGenerate}
            disabled={generating || (stats.total_weapons || 0) === 0}
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-mono text-xs uppercase tracking-wider py-3 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all btn-clip"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            GÉNÉRER MASTER SCRIPT
          </button>
        </div>

        {/* AI Expert Quick Access */}
        <div className="bg-card border border-border p-6 corner-brackets">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-accent/20 border border-accent/50 flex items-center justify-center">
              <Target className="w-6 h-6 text-accent" />
            </div>
            <div>
              <h3 className="font-heading text-lg font-bold">IA EXPERTE</h3>
              <p className="text-[10px] text-muted-foreground font-mono">ARCHITECTE BALISTIQUE</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Demande à l'IA de créer des scripts personnalisés, de suggérer des builds "méta cachés" ou d'optimiser tes configurations.
          </p>
          <div className="space-y-2 mb-4 text-[10px] font-mono">
            <div className="flex justify-between">
              <span className="text-muted-foreground">MODÈLE</span>
              <span className="text-accent">GEMINI 3 FLASH</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">EXPERTISE</span>
              <span className="text-accent">GPC / WARZONE</span>
            </div>
          </div>
          <button
            data-testid="go-to-ai-btn"
            onClick={() => onNavigate('ai')}
            className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-mono text-xs uppercase tracking-wider py-3 flex items-center justify-center gap-2 transition-all btn-clip"
          >
            <Target className="w-4 h-4" />
            CONSULTER L'IA
          </button>
        </div>
      </div>

      {/* Category Breakdown */}
      {stats.categories && Object.keys(stats.categories).length > 0 && (
        <div className="bg-card border border-border p-6 corner-brackets">
          <h3 className="font-heading text-lg font-bold mb-4">RÉPARTITION PAR CATÉGORIE</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {Object.entries(stats.categories).map(([cat, count]) => (
              <div key={cat} className="bg-secondary/50 border border-border p-4 text-center">
                <p className="font-heading text-2xl font-bold text-primary">{count}</p>
                <p className="text-[10px] font-mono text-muted-foreground mt-1">{cat}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color, onClick }) {
  return (
    <div 
      onClick={onClick}
      className={`bg-card border border-border p-6 corner-brackets transition-all ${onClick ? 'cursor-pointer hover:border-primary/50' : ''}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">{label}</p>
          <p className={`font-heading text-3xl font-bold mt-1 ${color === 'primary' ? 'text-primary' : color === 'accent' ? 'text-accent' : 'text-destructive'}`}>
            {value}
          </p>
        </div>
        <div className={`w-12 h-12 border flex items-center justify-center ${
          color === 'primary' ? 'bg-primary/20 border-primary/50' : 
          color === 'accent' ? 'bg-accent/20 border-accent/50' : 
          'bg-destructive/20 border-destructive/50'
        }`}>
          <Icon className={`w-6 h-6 ${
            color === 'primary' ? 'text-primary' : 
            color === 'accent' ? 'text-accent' : 
            'text-destructive'
          }`} />
        </div>
      </div>
    </div>
  );
}

// ============== META CENTER COMPONENT ==============
function MetaCenter({ weapons, onRefresh, onWeaponCreate, onWeaponUpdate, onWeaponDelete, onSeedWeapons }) {
  const [filter, setFilter] = useState({ category: '', game: '', metaType: '' });
  const [showForm, setShowForm] = useState(false);
  const [editingWeapon, setEditingWeapon] = useState(null);
  const [seeding, setSeeding] = useState(false);

  const categories = ['AR', 'SMG', 'LMG', 'SNIPER', 'SHOTGUN', 'PISTOL', 'LAUNCHER'];
  const games = ['BO6', 'MW3'];

  const filteredWeapons = weapons.filter(w => {
    if (filter.category && w.category !== filter.category) return false;
    if (filter.game && w.game !== filter.game) return false;
    if (filter.metaType === 'meta' && !w.is_meta) return false;
    if (filter.metaType === 'hidden' && !w.is_hidden_meta) return false;
    return true;
  });

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await onSeedWeapons();
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="font-heading text-3xl font-bold text-primary text-glow tracking-wider">META CENTER</h2>
          <p className="text-sm text-muted-foreground font-mono mt-1">BASE DE DONNÉES D'ARMES WARZONE</p>
        </div>
        <div className="flex gap-2">
          {weapons.length === 0 && (
            <button
              data-testid="seed-weapons-btn"
              onClick={handleSeed}
              disabled={seeding}
              className="bg-accent hover:bg-accent/90 text-accent-foreground font-mono text-xs uppercase tracking-wider px-4 py-2 flex items-center gap-2 disabled:opacity-50"
            >
              {seeding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />}
              CHARGER ARMES
            </button>
          )}
          <button
            data-testid="add-weapon-btn"
            onClick={() => { setEditingWeapon(null); setShowForm(true); }}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-mono text-xs uppercase tracking-wider px-4 py-2 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            AJOUTER
          </button>
          <button
            onClick={onRefresh}
            className="bg-secondary hover:bg-secondary/80 text-foreground font-mono text-xs uppercase tracking-wider px-4 py-2 flex items-center gap-2 border border-border"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <select
          data-testid="filter-category"
          value={filter.category}
          onChange={(e) => setFilter(f => ({ ...f, category: e.target.value }))}
          className="bg-secondary border border-border px-4 py-2 font-mono text-xs focus:border-primary outline-none"
        >
          <option value="">TOUTES CATÉGORIES</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select
          data-testid="filter-game"
          value={filter.game}
          onChange={(e) => setFilter(f => ({ ...f, game: e.target.value }))}
          className="bg-secondary border border-border px-4 py-2 font-mono text-xs focus:border-primary outline-none"
        >
          <option value="">TOUS JEUX</option>
          {games.map(g => <option key={g} value={g}>{g}</option>)}
        </select>
        <select
          data-testid="filter-meta-type"
          value={filter.metaType}
          onChange={(e) => setFilter(f => ({ ...f, metaType: e.target.value }))}
          className="bg-secondary border border-border px-4 py-2 font-mono text-xs focus:border-primary outline-none"
        >
          <option value="">TOUS TYPES</option>
          <option value="meta">META ACTUEL 🌟</option>
          <option value="hidden">META CACHÉ 🔴</option>
        </select>
        <div className="flex-1 text-right text-sm text-muted-foreground font-mono">
          {filteredWeapons.length} arme(s)
        </div>
      </div>

      {/* Weapons Grid */}
      {filteredWeapons.length === 0 ? (
        <div className="bg-card border border-border p-12 text-center">
          <Database className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground font-mono">Aucune arme dans la base de données</p>
          <p className="text-sm text-muted-foreground mt-2">Cliquez sur "CHARGER ARMES" pour importer les armes par défaut</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredWeapons.map(weapon => (
            <WeaponCard
              key={weapon.id}
              weapon={weapon}
              onEdit={() => { setEditingWeapon(weapon); setShowForm(true); }}
              onDelete={() => onWeaponDelete(weapon.id)}
            />
          ))}
        </div>
      )}

      {/* Weapon Form Modal */}
      {showForm && (
        <WeaponForm
          weapon={editingWeapon}
          onSave={async (data) => {
            if (editingWeapon) {
              await onWeaponUpdate(editingWeapon.id, data);
            } else {
              await onWeaponCreate(data);
            }
            setShowForm(false);
            setEditingWeapon(null);
          }}
          onClose={() => { setShowForm(false); setEditingWeapon(null); }}
        />
      )}
    </div>
  );
}

function WeaponCard({ weapon, onEdit, onDelete }) {
  const [showDelete, setShowDelete] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [optimizedData, setOptimizedData] = useState(null);
  const [loadingOptimized, setLoadingOptimized] = useState(false);
  
  // Calculate TTK (Time To Kill) - estimation simple
  const calculateTTK = () => {
    if (!weapon.damage || !weapon.fire_rate) return 'N/A';
    // Assume 250 HP, calculate shots to kill
    const shotsToKill = Math.ceil(250 / weapon.damage);
    // Calculate time in ms (60000ms / fire_rate * (shots - 1))
    const ttk = Math.round((60000 / weapon.fire_rate) * (shotsToKill - 1));
    return `${ttk}ms`;
  };

  const loadOptimizedStats = async () => {
    setLoadingOptimized(true);
    try {
      const response = await axios.get(`${BACKEND_URL}/api/weapons/${weapon.id}/optimized`);
      setOptimizedData(response.data);
      setShowDetail(true);
    } catch (error) {
      toast.error('Erreur chargement stats optimisées');
    } finally {
      setLoadingOptimized(false);
    }
  };

  return (
    <div className="bg-card border border-border p-4 corner-brackets group hover:border-primary/30 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-heading text-lg font-bold glitch-hover">{weapon.name}</h3>
            {weapon.is_meta && <span className="text-[9px] bg-primary/20 text-primary px-1.5 py-0.5 font-mono">META</span>}
            {weapon.is_hidden_meta && <span className="text-[9px] bg-destructive/20 text-destructive px-1.5 py-0.5 font-mono animate-pulse">HIDDEN</span>}
          </div>
          <div className="flex gap-2 mt-1">
            <span className="text-[10px] bg-secondary px-2 py-0.5 font-mono text-muted-foreground">{weapon.category}</span>
            <span className="text-[10px] bg-secondary px-2 py-0.5 font-mono text-muted-foreground">{weapon.game}</span>
          </div>
        </div>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            data-testid={`edit-weapon-${weapon.id}`}
            onClick={onEdit}
            className="p-1.5 hover:bg-primary/20 text-muted-foreground hover:text-primary transition-colors"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            data-testid={`delete-weapon-${weapon.id}`}
            onClick={() => setShowDelete(true)}
            className="p-1.5 hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 text-[10px] font-mono mb-3">
        <div className="bg-secondary/50 p-2">
          <span className="text-muted-foreground">RECUL V</span>
          <p className="text-primary font-bold text-lg">{weapon.vertical_recoil}</p>
        </div>
        <div className="bg-secondary/50 p-2">
          <span className="text-muted-foreground">RECUL H</span>
          <p className="text-accent font-bold text-lg">{weapon.horizontal_recoil}</p>
        </div>
        <div className="bg-secondary/50 p-2">
          <span className="text-muted-foreground">TTK</span>
          <p className="text-destructive font-bold text-lg">{calculateTTK()}</p>
        </div>
        <div className="bg-secondary/50 p-2">
          <span className="text-muted-foreground">CADENCE</span>
          <p className="text-foreground">{weapon.fire_rate} RPM</p>
        </div>
        <div className="bg-secondary/50 p-2">
          <span className="text-muted-foreground">DÉGÂTS</span>
          <p className="text-foreground">{weapon.damage}</p>
        </div>
        <div className="bg-secondary/50 p-2">
          <span className="text-muted-foreground">PORTÉE</span>
          <p className="text-foreground">{weapon.range_meters}m</p>
        </div>
      </div>

      {/* Rapid Fire indicator */}
      {weapon.rapid_fire && (
        <div className="text-[10px] font-mono text-accent mb-2 flex items-center gap-1 bg-accent/10 p-2 border border-accent/30">
          <Zap className="w-3 h-3" />
          RAPID FIRE: {weapon.rapid_fire_value}ms
        </div>
      )}

      {/* Recommended Build - HIGHLIGHTED */}
      {weapon.recommended_build && (
        <div className="bg-primary/5 border border-primary/20 p-3 rounded mb-2">
          <div className="text-[10px] text-primary font-mono font-bold mb-1 flex items-center gap-1">
            <Settings className="w-3 h-3" />
            BUILD META:
          </div>
          <div className="text-[11px] text-foreground leading-relaxed">
            {weapon.recommended_build}
          </div>
        </div>
      )}

      {/* Notes */}
      {weapon.notes && (
        <div className="text-[10px] text-muted-foreground italic mt-2 border-t border-border pt-2">
          💡 {weapon.notes}
        </div>
      )}

      {/* NOUVEAU: Bouton voir build optimisé */}
      <button
        onClick={loadOptimizedStats}
        disabled={loadingOptimized}
        className="w-full mt-3 bg-accent/20 hover:bg-accent/30 border border-accent/50 text-accent font-mono text-[10px] uppercase py-2 flex items-center justify-center gap-2 transition-all"
      >
        {loadingOptimized ? (
          <Loader2 className="w-3 h-3 animate-spin" />
        ) : (
          <Target className="w-3 h-3" />
        )}
        BUILD CRONUS OPTIMAL
      </button>

      {/* Delete Confirmation */}
      {showDelete && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={() => setShowDelete(false)}>
          <div className="bg-card border border-border p-6 max-w-sm" onClick={e => e.stopPropagation()}>
            <h3 className="font-heading text-lg mb-4">CONFIRMER SUPPRESSION</h3>
            <p className="text-sm text-muted-foreground mb-4">Supprimer {weapon.name} de la base de données?</p>
            <div className="flex gap-2">
              <button
                onClick={() => { onDelete(); setShowDelete(false); }}
                className="flex-1 bg-destructive hover:bg-destructive/90 text-white font-mono text-xs py-2"
              >
                SUPPRIMER
              </button>
              <button
                onClick={() => setShowDelete(false)}
                className="flex-1 bg-secondary hover:bg-secondary/80 font-mono text-xs py-2 border border-border"
              >
                ANNULER
              </button>
            </div>
          </div>
        </div>
      )}

      {/* NOUVEAU: Modal Build Optimisé */}
      {showDetail && optimizedData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" onClick={() => setShowDetail(false)}>
          <div className="bg-card border-2 border-accent p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto corner-brackets" onClick={e => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-heading font-bold glitch-hover mb-2">{weapon.name}</h2>
                <div className="flex gap-2">
                  <span className="text-[10px] bg-secondary px-2 py-1 font-mono">{weapon.category}</span>
                  {weapon.is_hidden_meta && <span className="text-[10px] bg-destructive/20 text-destructive px-2 py-1 font-mono animate-pulse">🔴 META CACHÉ</span>}
                </div>
              </div>
              <button onClick={() => setShowDetail(false)} className="text-muted-foreground hover:text-foreground transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="bg-accent/10 border-2 border-accent/50 p-4 mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-5 h-5 text-accent" />
                <h3 className="text-lg font-heading font-bold text-accent">BUILD CRONUS (MAX TTK)</h3>
              </div>
              <div className="text-sm font-mono leading-relaxed bg-card/50 p-3 border border-accent/30">{optimizedData.build}</div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-secondary/30 border border-border p-4">
                <h4 className="text-xs font-mono text-muted-foreground uppercase mb-3">⚪ SANS CRONUS</h4>
                <div className="space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span className="text-muted-foreground">TTK:</span><span className="font-bold">{optimizedData.base_stats.ttk}ms</span></div>
                </div>
              </div>
              <div className="bg-accent/10 border-2 border-accent p-4">
                <h4 className="text-xs font-mono text-accent uppercase mb-3">🔥 AVEC CRONUS</h4>
                <div className="space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span className="text-muted-foreground">TTK:</span><span className="text-accent font-bold text-lg">{optimizedData.optimized_stats.ttk}ms</span></div>
                </div>
              </div>
            </div>

            <div className="bg-primary/10 border-2 border-primary p-4 mb-4">
              <div className="flex items-center justify-between">
                <div><div className="text-xs font-mono text-muted-foreground">AVANTAGE</div><div className="text-2xl font-heading font-bold text-primary">-{optimizedData.improvement.ttk_saved_ms}ms</div></div>
                <div className="text-right"><div className="text-xs font-mono text-muted-foreground">TUE + VITE</div><div className="text-2xl font-heading font-bold text-primary">{optimizedData.improvement.ttk_improvement_percent}%</div></div>
              </div>
            </div>

            <div className="flex gap-3">
              <button onClick={() => { navigator.clipboard.writeText(optimizedData.build); toast.success('Build copié !'); }} className="flex-1 bg-primary/20 hover:bg-primary/30 border border-primary text-primary px-4 py-3 font-mono text-xs uppercase flex items-center justify-center gap-2">
                <Copy className="w-4 h-4" />COPIER BUILD
              </button>
              <button onClick={() => setShowDetail(false)} className="flex-1 bg-secondary hover:bg-secondary/80 px-4 py-3 font-mono text-xs uppercase">FERMER</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function WeaponForm({ weapon, onSave, onClose }) {
  const [form, setForm] = useState({
    name: weapon?.name || '',
    category: weapon?.category || 'AR',
    game: weapon?.game || 'BO6',
    vertical_recoil: weapon?.vertical_recoil || 25,
    horizontal_recoil: weapon?.horizontal_recoil || 10,
    fire_rate: weapon?.fire_rate || 700,
    damage: weapon?.damage || 30,
    range_meters: weapon?.range_meters || 40,
    rapid_fire: weapon?.rapid_fire || false,
    rapid_fire_value: weapon?.rapid_fire_value || 0,
    recommended_build: weapon?.recommended_build || '',
    notes: weapon?.notes || '',
    is_meta: weapon?.is_meta || false,
    is_hidden_meta: weapon?.is_hidden_meta || false,
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(form);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-card border border-border p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-heading text-xl font-bold text-primary">
            {weapon ? 'MODIFIER ARME' : 'NOUVELLE ARME'}
          </h3>
          <button onClick={onClose} className="p-2 hover:bg-secondary">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] font-mono text-muted-foreground mb-1">NOM DE L'ARME *</label>
              <input
                data-testid="weapon-name-input"
                type="text"
                value={form.name}
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                required
                className="w-full bg-secondary border border-border px-4 py-2 font-mono text-sm focus:border-primary outline-none"
                placeholder="XM4"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] font-mono text-muted-foreground mb-1">CATÉGORIE</label>
                <select
                  data-testid="weapon-category-select"
                  value={form.category}
                  onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                  className="w-full bg-secondary border border-border px-3 py-2 font-mono text-sm focus:border-primary outline-none"
                >
                  {['AR', 'SMG', 'LMG', 'SNIPER', 'SHOTGUN', 'PISTOL', 'LAUNCHER'].map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-[10px] font-mono text-muted-foreground mb-1">JEU</label>
                <select
                  data-testid="weapon-game-select"
                  value={form.game}
                  onChange={e => setForm(f => ({ ...f, game: e.target.value }))}
                  className="w-full bg-secondary border border-border px-3 py-2 font-mono text-sm focus:border-primary outline-none"
                >
                  <option value="BO6">BO6</option>
                  <option value="MW3">MW3</option>
                </select>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-[10px] font-mono text-muted-foreground mb-1">RECUL VERTICAL</label>
              <input
                data-testid="weapon-vrecoil-input"
                type="number"
                value={form.vertical_recoil}
                onChange={e => setForm(f => ({ ...f, vertical_recoil: parseInt(e.target.value) || 0 }))}
                className="w-full bg-secondary border border-border px-4 py-2 font-mono text-sm focus:border-primary outline-none"
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono text-muted-foreground mb-1">RECUL HORIZONTAL</label>
              <input
                data-testid="weapon-hrecoil-input"
                type="number"
                value={form.horizontal_recoil}
                onChange={e => setForm(f => ({ ...f, horizontal_recoil: parseInt(e.target.value) || 0 }))}
                className="w-full bg-secondary border border-border px-4 py-2 font-mono text-sm focus:border-primary outline-none"
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono text-muted-foreground mb-1">CADENCE (RPM)</label>
              <input
                data-testid="weapon-firerate-input"
                type="number"
                value={form.fire_rate}
                onChange={e => setForm(f => ({ ...f, fire_rate: parseInt(e.target.value) || 0 }))}
                className="w-full bg-secondary border border-border px-4 py-2 font-mono text-sm focus:border-primary outline-none"
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono text-muted-foreground mb-1">DÉGÂTS</label>
              <input
                data-testid="weapon-damage-input"
                type="number"
                value={form.damage}
                onChange={e => setForm(f => ({ ...f, damage: parseInt(e.target.value) || 0 }))}
                className="w-full bg-secondary border border-border px-4 py-2 font-mono text-sm focus:border-primary outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] font-mono text-muted-foreground mb-1">BUILD RECOMMANDÉ</label>
              <textarea
                data-testid="weapon-build-input"
                value={form.recommended_build}
                onChange={e => setForm(f => ({ ...f, recommended_build: e.target.value }))}
                rows={2}
                className="w-full bg-secondary border border-border px-4 py-2 font-mono text-sm focus:border-primary outline-none resize-none"
                placeholder="Compensator + Long Barrel + Vertical Foregrip..."
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono text-muted-foreground mb-1">NOTES</label>
              <textarea
                data-testid="weapon-notes-input"
                value={form.notes}
                onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                rows={2}
                className="w-full bg-secondary border border-border px-4 py-2 font-mono text-sm focus:border-primary outline-none resize-none"
                placeholder="Notes spéciales sur cette arme..."
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.rapid_fire}
                onChange={e => setForm(f => ({ ...f, rapid_fire: e.target.checked }))}
                className="w-4 h-4 accent-primary"
              />
              <span className="text-sm font-mono">RAPID FIRE</span>
            </label>
            {form.rapid_fire && (
              <input
                type="number"
                value={form.rapid_fire_value}
                onChange={e => setForm(f => ({ ...f, rapid_fire_value: parseInt(e.target.value) || 0 }))}
                placeholder="Délai (ms)"
                className="bg-secondary border border-border px-3 py-1 font-mono text-sm focus:border-primary outline-none w-24"
              />
            )}
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_meta}
                onChange={e => setForm(f => ({ ...f, is_meta: e.target.checked }))}
                className="w-4 h-4 accent-primary"
              />
              <span className="text-sm font-mono">META</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_hidden_meta}
                onChange={e => setForm(f => ({ ...f, is_hidden_meta: e.target.checked }))}
                className="w-4 h-4 accent-destructive"
              />
              <span className="text-sm font-mono">HIDDEN META</span>
            </label>
          </div>

          <div className="flex gap-2 pt-4">
            <button
              data-testid="save-weapon-btn"
              type="submit"
              disabled={saving || !form.name}
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-mono text-xs uppercase tracking-wider py-3 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              SAUVEGARDER
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 bg-secondary hover:bg-secondary/80 font-mono text-xs uppercase tracking-wider py-3 border border-border"
            >
              ANNULER
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============== AI EXPERT COMPONENT ==============
function AIExpert({ weapons }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || sending) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setSending(true);

    try {
      const response = await api.sendMessage(sessionId, userMessage);
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      toast.error("Erreur de communication avec l'IA");
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Désolé, une erreur s'est produite. Réessayez." 
      }]);
    } finally {
      setSending(false);
    }
  };

  const quickPrompts = [
    "Génère un script anti-recoil pour le XM4 avec support OLED",
    "Quelle est l'arme méta cachée avec le meilleur TTK?",
    "Crée un Master Script avec détection automatique ADT",
    "Build optimal pour le WSP Swarm avec rapid fire?",
  ];

  return (
    <div className="h-full flex flex-col fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="font-heading text-3xl font-bold text-accent text-glow tracking-wider">IA EXPERTE</h2>
          <p className="text-sm text-muted-foreground font-mono mt-1">ARCHITECTE BALISTIQUE WARZONE</p>
        </div>
        <div className="text-[10px] font-mono text-muted-foreground">
          {weapons.length} armes en contexte
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 bg-card border border-border flex flex-col min-h-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <Target className="w-16 h-16 text-accent/30 mb-4" />
              <h3 className="font-heading text-xl text-muted-foreground mb-2">ARCHITECTE BALISTIQUE</h3>
              <p className="text-sm text-muted-foreground max-w-md mb-6">
                Pose-moi n'importe quelle question sur les scripts Cronus, les builds d'armes, ou demande-moi de générer du code GPC personnalisé.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 w-full max-w-2xl">
                {quickPrompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(prompt)}
                    className="text-left text-xs font-mono p-3 bg-secondary/50 border border-border hover:border-accent/50 hover:bg-accent/5 transition-all"
                  >
                    <ChevronRight className="w-3 h-3 inline mr-2 text-accent" />
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-4 ${
                    msg.role === 'user'
                      ? 'bg-primary/20 border border-primary/30'
                      : 'bg-secondary border border-border'
                  }`}
                >
                  <div className="text-[10px] font-mono text-muted-foreground mb-2">
                    {msg.role === 'user' ? 'VOUS' : 'IA EXPERTE'}
                  </div>
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                  {msg.role === 'assistant' && msg.content.includes('define ') && (
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(msg.content);
                        toast.success('Code copié!');
                      }}
                      className="mt-2 text-[10px] font-mono text-accent hover:text-accent/80 flex items-center gap-1"
                    >
                      <Copy className="w-3 h-3" /> COPIER LE CODE
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-secondary border border-border p-4">
                <Loader2 className="w-5 h-5 animate-spin text-accent" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-border p-4">
          <div className="flex gap-2">
            <input
              data-testid="chat-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Demande un script, un build, ou pose une question..."
              className="flex-1 bg-secondary border border-border px-4 py-3 font-mono text-sm focus:border-accent outline-none"
              disabled={sending}
            />
            <button
              data-testid="send-message-btn"
              onClick={sendMessage}
              disabled={sending || !input.trim()}
              className="bg-accent hover:bg-accent/90 text-accent-foreground px-6 py-3 font-mono text-xs uppercase tracking-wider flex items-center gap-2 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============== SCRIPTS VAULT COMPONENT ==============
function ScriptsVault({ scripts, onRefresh, onDelete }) {
  const [selectedScript, setSelectedScript] = useState(null);

  const copyToClipboard = (code) => {
    navigator.clipboard.writeText(code);
    toast.success('Script copié dans le presse-papier!');
  };

  const downloadScript = (script) => {
    const blob = new Blob([script.code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${script.title}.gpc`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Script téléchargé!');
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-heading text-3xl font-bold text-primary text-glow tracking-wider">COFFRE-FORT</h2>
          <p className="text-sm text-muted-foreground font-mono mt-1">SCRIPTS GPC SAUVEGARDÉS</p>
        </div>
        <button
          onClick={onRefresh}
          className="bg-secondary hover:bg-secondary/80 text-foreground font-mono text-xs uppercase tracking-wider px-4 py-2 flex items-center gap-2 border border-border"
        >
          <RefreshCw className="w-4 h-4" />
          ACTUALISER
        </button>
      </div>

      {/* Scripts List */}
      {scripts.length === 0 ? (
        <div className="bg-card border border-border p-12 text-center">
          <Archive className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground font-mono">Aucun script sauvegardé</p>
          <p className="text-sm text-muted-foreground mt-2">Utilisez l'IA Experte ou le Master Engine pour générer des scripts</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scripts.map(script => (
            <div key={script.id} className="bg-card border border-border p-4 corner-brackets group hover:border-primary/30 transition-all">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-heading text-sm font-bold">{script.title}</h3>
                  <div className="flex gap-2 mt-1">
                    <span className={`text-[9px] px-1.5 py-0.5 font-mono ${
                      script.script_type === 'master' ? 'bg-accent/20 text-accent' : 'bg-primary/20 text-primary'
                    }`}>
                      {script.script_type.toUpperCase()}
                    </span>
                    {script.weapon_ids?.length > 0 && (
                      <span className="text-[9px] bg-secondary px-1.5 py-0.5 font-mono text-muted-foreground">
                        {script.weapon_ids.length} ARMES
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="text-[9px] text-muted-foreground font-mono mb-3">
                {new Date(script.created_at).toLocaleString('fr-FR')}
              </div>

              <div className="bg-background border border-border p-2 h-24 overflow-hidden text-[9px] font-mono text-muted-foreground mb-3">
                {script.code.slice(0, 200)}...
              </div>

              <div className="flex gap-2">
                <button
                  data-testid={`view-script-${script.id}`}
                  onClick={() => setSelectedScript(script)}
                  className="flex-1 bg-secondary hover:bg-secondary/80 text-foreground font-mono text-[10px] uppercase py-2 flex items-center justify-center gap-1 border border-border"
                >
                  <Eye className="w-3 h-3" /> VOIR
                </button>
                <button
                  onClick={() => copyToClipboard(script.code)}
                  className="p-2 bg-secondary hover:bg-primary/20 border border-border hover:border-primary/50 transition-all"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={() => downloadScript(script)}
                  className="p-2 bg-secondary hover:bg-accent/20 border border-border hover:border-accent/50 transition-all"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  data-testid={`delete-script-${script.id}`}
                  onClick={() => onDelete(script.id)}
                  className="p-2 bg-secondary hover:bg-destructive/20 border border-border hover:border-destructive/50 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Script Viewer Modal */}
      {selectedScript && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4" onClick={() => setSelectedScript(null)}>
          <div className="bg-card border border-border p-6 max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-heading text-xl font-bold text-primary">{selectedScript.title}</h3>
                <p className="text-[10px] font-mono text-muted-foreground mt-1">
                  {selectedScript.script_type.toUpperCase()} • {new Date(selectedScript.created_at).toLocaleString('fr-FR')}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(selectedScript.code)}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 font-mono text-xs flex items-center gap-2"
                >
                  <Copy className="w-4 h-4" /> COPIER
                </button>
                <button
                  onClick={() => downloadScript(selectedScript)}
                  className="bg-accent hover:bg-accent/90 text-accent-foreground px-4 py-2 font-mono text-xs flex items-center gap-2"
                >
                  <Download className="w-4 h-4" /> TÉLÉCHARGER
                </button>
                <button onClick={() => setSelectedScript(null)} className="p-2 hover:bg-secondary">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-auto bg-background border border-border p-4">
              <pre className="font-mono text-xs whitespace-pre text-foreground">{selectedScript.code}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============== MAIN APP ==============
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [weapons, setWeapons] = useState([]);
  const [scripts, setScripts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  // Load data
  const loadData = useCallback(async () => {
    try {
      const [weaponsRes, scriptsRes, statsRes] = await Promise.all([
        api.getWeapons(),
        api.getScripts(),
        api.getStats(),
      ]);
      setWeapons(weaponsRes.data);
      setScripts(scriptsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error("Erreur de chargement des données");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Weapon handlers
  const handleCreateWeapon = async (data) => {
    try {
      await api.createWeapon(data);
      toast.success('Arme créée!');
      loadData();
    } catch (error) {
      toast.error("Erreur lors de la création");
    }
  };

  const handleUpdateWeapon = async (id, data) => {
    try {
      await api.updateWeapon(id, data);
      toast.success('Arme mise à jour!');
      loadData();
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  const handleDeleteWeapon = async (id) => {
    try {
      await api.deleteWeapon(id);
      toast.success('Arme supprimée!');
      loadData();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleSeedWeapons = async () => {
    try {
      const response = await api.seedWeapons();
      if (response.data.seeded) {
        toast.success(`${response.data.count} armes importées!`);
        loadData();
      } else {
        toast.info(response.data.message);
      }
    } catch (error) {
      toast.error("Erreur lors de l'import");
    }
  };

  // Script handlers
  const handleDeleteScript = async (id) => {
    try {
      await api.deleteScript(id);
      toast.success('Script supprimé!');
      loadData();
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleGenerateMasterScript = async () => {
    try {
      const response = await api.generateMasterScript();
      toast.success(`Master Script généré avec ${response.data.weapon_count} armes!`);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de la génération");
    }
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <p className="font-mono text-sm text-muted-foreground">INITIALISATION DU SYSTÈME...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-background scanlines">
      <Toaster 
        theme="dark" 
        position="top-right"
        toastOptions={{
          style: {
            background: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            color: 'hsl(var(--foreground))',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '12px',
          },
        }}
      />
      
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} stats={stats} />
      
      <main className="flex-1 overflow-y-auto p-6 grid-bg">
        {activeTab === 'dashboard' && (
          <Dashboard 
            stats={stats} 
            onNavigate={setActiveTab}
            onGenerateMaster={handleGenerateMasterScript}
          />
        )}
        {activeTab === 'meta' && (
          <MetaCenter 
            weapons={weapons}
            onRefresh={loadData}
            onWeaponCreate={handleCreateWeapon}
            onWeaponUpdate={handleUpdateWeapon}
            onWeaponDelete={handleDeleteWeapon}
            onSeedWeapons={handleSeedWeapons}
          />
        )}
        {activeTab === 'ai' && (
          <AIExpert weapons={weapons} />
        )}
        {activeTab === 'scripts' && (
          <ScriptsVault 
            scripts={scripts}
            onRefresh={loadData}
            onDelete={handleDeleteScript}
          />
        )}
      </main>
    </div>
  );
}

export default App;
