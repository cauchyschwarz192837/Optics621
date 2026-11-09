"""Error summaries and finite-trial binomial intervals."""
import numpy as np
from scipy.stats import beta


def interval(k,n,alpha=.05):
    return (0. if k==0 else float(beta.ppf(alpha/2,k,n-k+1)),
            1. if k==n else float(beta.ppf(1-alpha/2,k+1,n-k)))


def summarize(ranges,true_range,resolution,scores,threshold):
    error=np.asarray(ranges)-true_range; n=len(error)
    failed=int(np.sum(abs(error)>resolution/2))
    detected=int(np.sum(np.asarray(scores)>threshold))
    return dict(n=n,bias_m=float(error.mean()),std_m=float(error.std(ddof=1)) if n>1 else 0.,
        rmse_m=float(np.sqrt(np.mean(error**2))),gross_error_probability=failed/n,
        gross_error_ci95=interval(failed,n),detection_probability=detected/n,
        detection_ci95=interval(detected,n),threshold=float(threshold))
