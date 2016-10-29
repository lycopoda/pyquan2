import init, os, warnings, sys
import noise_reduction as noise
import peak_pars as pars
from scipy.optimize import OptimizeWarning

    

class Project(object):
    def __init__(self, project_name, init_file='pyquan.ini'):
        self._project_name = project_name
        self._info = init.Info(init_file)
        self._path = init.Path(project_name, self._info)
        self._csv = self._info.csv
        self._runlist = self._path.runlist_cal
        info = self._info
        self.get_CFdict()
        self._noise = noise.NoiseReduction(info)
        self._fit_peak = info.fit_peak
        self._param = pars.Pars(info)
        self.create_dir()
        warnings.simplefilter('error', OptimizeWarning)

    @property
    def csv(self):
        return self._csv

    @property
    def project_name(self):
        return self._project_name

    @property
    def path(self):
        return self._path

    @property
    def info(self):
        return self._info

    @property
    def runlist(self):
        return self._runlist

    @property
    def fit_peak(self):
        return self._fit_peak

    @property
    def noise(self):
        return self._noise

    @property
    def lib(self):
        return self._lib

    @property
    def CFdict(self):
        return self._CFdict

    @property
    def RTdict(self):
        return self._RTdict

    def mz(self, code):
        return self._lib._lib[code]['mz']

    def create_dir(self):
        dir_list = ['project_dir', 'amdis_dir', 'align_dir', 'data_dir',
                    'images_dir','norm_dir']
        for item in dir_list:
            item_dir = getattr(self._path, item)
            if not os.path.exists(item_dir):
                os.mkdir(item_dir)
        return

    def read_library(self):
        import library
        self._lib = library.Library(self._path.library_file, self._csv)
        return

    def get_CFdict(self):
        self._CFdict = {}
        if not os.path.exists(self._path.runlist_file):
            print('ERROR: No calibration file, run calibrate.py')
            sys.exit(2)
        with open(self._path.runlist_file, 'r') as runlist:
            for line in runlist:
                info = self._csv.read_line(line)
                sample = info[0].lower()
                if sample in self._runlist:
                    try:
                        CV = (float(info[-2]), float(info[-1]))
                    except ValueError:
                        print('ERROR: {0} corrupted'.format(self._path.runlist))
                        sys.exit(2)
                    self._CFdict[sample] = CV
        return

    def get_RTdict(self):
        self._RTdict = {}
        self.read_amdis()
        if self._info.min_fit:
            import backfill
            self._RTdict = backfill.bf(self, 
                                       threshold=self._info.min_fit)
        return

    def read_amdis(self, code=None):
        import amdis
        for sample in self._runlist:
            path = self._path.amdis_file_sample(sample)
            amdis_sample = amdis.Sample(path, library=self._lib,
                                        CF=self._CFdict[sample])
            self._RTdict[sample] = amdis_sample.data()
        return


class Project_cp(Project):
    def __init__(self, project_name, check_peak, init_file='pyquan.ini'):
        super().__init__(project_name, init_file)
        self._check_peak =  check_peak

    def get_RTdict(self):
        self._RTdict = {}
        self.read_amdis()
        code = self._check_peak.code
        for sample in self._RTdict:
            try:
                code_value = self._RTdict[sample][code]
            except KeyError:
                code_value = None
            self._RTdict[sample].clear()
            self._RTdict[sample][code] = code_value
        if not self._check_peak.sample:
            import backfill
            backfill.bf(self, threshold=-1, code=code)
        return

