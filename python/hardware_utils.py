from     datetime   import datetime, timedelta
from     pathlib    import Path
import   psutil
import   torch
import   json
import   logging
logger = logging.getLogger(__name__)
#=========================================================================
# Konfiguration (Pfad, Powerlevel-Mapping, Refresh-Zeit)

HARDWARE_CACHE_PATH  = Path(__file__).resolve().parents[2] / "hardware_cache.json"
LLM_CONFIG           = {
    "high":   {"n_ctx": 4096, "n_threads": 12, "n_gpu_layers": 20},  # 8-10
    "medium": {"n_ctx": 4096, "n_threads": 8,  "n_gpu_layers": 0 },  # 4-7
    "low":    {"n_ctx": 2048, "n_threads": 4,  "n_gpu_layers": 0 },  # 0-3
}
CACHE_MAX_AGE_DAYS   = 30

#=========================================================================
class HardwareManager:

    def __init__(self):

        self._power         : int               = None
        self._specs         : dict              = None
        self._llm_config    : dict              = None
        self._cached_at     : datetime | None   = None

#-------------------------------------------------------------------------
# Öffentliche Schnittstelle

    @property
    def specs(self) -> dict:
        if self._specs is None:
            self._load()
        return self._specs
    
    @property
    def power_level(self) -> int:
        if self._power is None:
            self._load()
        return self._power

    @property
    def llm_config(self) -> dict:
        if self._llm_config is None:
            self._load()
        return self._llm_config

    def refresh(self) -> None:
        '''Cache löschen und neu einlesen.'''
        if HARDWARE_CACHE_PATH.exists():
            HARDWARE_CACHE_PATH.unlink()
        self._specs      = None
        self._power      = None
        self._llm_config = None
        self._load()

#-------------------------------------------------------------------------
# Private Methoden

    def _load(self) -> None:
        '''Erstellt wenn nicht vorhanden oder lädt Chache.'''
        if HARDWARE_CACHE_PATH.exists():
            try:
                self._read_cache()
                
                if self._is_expired():
                    logger.info("Hardware cache expired, regenerating.")
                    self.refresh()
                    return
                
                logger.info("Hardware config loaded from cache.")
                return
            
            except Exception as e:
                logger.warning(f"Cache unreadable, regenerating: {e}")

        self._detect_and_cache()

    def _detect_and_cache(self) -> None:
        '''Ermittelt Hardware, berechnet Power Level und schreibt Cache.'''
        specs       = self._get_specs()
        power       = self._estimate_power(specs)
        llm_config  = self._get_llm_config(power)

        self._specs      = specs
        self._power      = power
        self._llm_config = llm_config

        data = {
            "specs": specs, 
            "power_level": power, 
            "llm_config": llm_config,
            "cached_at": datetime.now().isoformat()
            }
        
        try:
            with open(HARDWARE_CACHE_PATH, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Hardware cache written. Power level: {power}")
        except Exception as e:
            logger.warning(f"Could not write hardware cache: {e}")

    def _read_cache(self) -> None:
        with open(HARDWARE_CACHE_PATH, "r") as f:
            data = json.load(f)
        self._specs      = data["specs"]
        self._power      = data["power_level"]
        self._llm_config = data["llm_config"]
        self._cached_at  = datetime.fromisoformat(data["cached_at"])

    def _get_specs(self) -> dict:
        ram_gb    = psutil.virtual_memory().total / 1e9
        cpu_cores = psutil.cpu_count(logical=True)

        if torch.cuda.is_available():
            gpu_name   = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            device     = "cuda"
        else:
            gpu_name   = None
            gpu_memory = 0.0
            device     = "cpu"

        return {
            "RAM_GB":       ram_gb,
            "CPU_Cores":    cpu_cores,
            "GPU_Name":     gpu_name,
            "GPU_Memory_GB": gpu_memory,
            "Device":       device,
        }

    def _estimate_power(self, specs: dict) -> int:
        score = 0

        if specs["RAM_GB"] >= 64:      score += 5
        elif specs["RAM_GB"] >= 32:    score += 4
        elif specs["RAM_GB"] >= 16:    score += 2
        else:                          score += 1

        if specs["CPU_Cores"] >= 16:   score += 3
        elif specs["CPU_Cores"] >= 8:  score += 2
        else:                          score += 1

        if specs["GPU_Memory_GB"] >= 24:    score += 3
        elif specs["GPU_Memory_GB"] >= 12:  score += 2
        elif specs["GPU_Memory_GB"] > 0:    score += 1

        return min(score, 10)

    def _get_llm_config(self, power: int) -> dict:
        if power >= 7:
            return LLM_CONFIG["high"]
        elif power >= 4:
            return LLM_CONFIG["medium"]
        else:
            return LLM_CONFIG["low"]

    def _is_expired(self) -> bool:
        if self._cached_at is None:
            return True
        age = datetime.now() - self._cached_at
        max_age = timedelta(days=CACHE_MAX_AGE_DAYS)
        return age > max_age