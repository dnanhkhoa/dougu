import os
import matplotlib as mpl
if os.environ.get('DISPLAY') is None:  # NOQA
    mpl.use('Agg')  # NOQA
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib
import itertools
import numpy as np

from pylab import rcParams
rcParams['figure.figsize'] = (12, 12)


# http://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html#the-seq2seq-model  # NOQA
def plot_attention(
        input_labels, output_labels, attentions,
        out_colors=None, filepath=None):
    # Set up figure with colorbar
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(attentions, cmap='bone')
    fig.colorbar(cax)

    # Set up axes
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.tick_params(axis='both', which='minor', labelsize=8)
    ax.set_xticklabels([''] + output_labels, rotation=90)
    ax.set_yticklabels([''] + input_labels)

    # Show label at every tick
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

    if out_colors:
        out_colors = ["k"] + out_colors
        assert len(out_colors) == 1 + len(output_labels), \
            f"got {len(out_colors)} colors for {len(output_labels)} labels"
        for xtick, color in zip(ax.get_xticklabels(), out_colors):
            xtick.set_color(color)

    if filepath:
        plt.savefig(filepath)
    else:
        plt.show()
    plt.close()


# http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html  # NOQA
def plot_confusion_matrix(
        cm, classes,
        normalize=False, title='Confusion matrix', cmap=plt.cm.Blues,
        filepath=None):
    """This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        plt.imshow(
            cm, interpolation='nearest', cmap=cmap, vmin=0, vmax=1)
    else:
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(
                j, i, f"{cm[i, j]:.2f}",
                horizontalalignment="center",
                color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    if filepath:
        plt.savefig(filepath)
    else:
        plt.show()
    plt.close()


# https://stackoverflow.com/questions/18195758/set-matplotlib-colorbar-size-to-match-graph  # NOQA
def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
    """Add a vertical color bar to an image plot."""
    from mpl_toolkits import axes_grid1
    divider = axes_grid1.make_axes_locatable(im.axes)
    width = axes_grid1.axes_size.AxesY(im.axes, aspect=1./aspect)
    pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
    current_ax = plt.gca()
    cax = divider.append_axes("right", size=width, pad=pad)
    plt.sca(current_ax)
    return im.axes.figure.colorbar(im, cax=cax, **kwargs)


def simple_imshow(
        matrix,
        cmap="viridis", figsize=(10, 10), aspect_equal=True, outfile=None,
        xlabel=None, ylabel=None,
        xtick_locs_labels=None, scale="lin"):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1)
    if aspect_equal:
        ax.set_aspect('equal')
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    norm = matplotlib.colors.SymLogNorm(1) if scale == "log" else None
    im = plt.imshow(matrix, interpolation='nearest', cmap=cmap, norm=norm)
    if xtick_locs_labels:
        plt.xticks(*xtick_locs_labels)
    add_colorbar(im)
    plt.tight_layout()
    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()


def plot_embeddings(
        emb, emb_method=None,
        labels=None, colors=None, classes=None, class2color=None,
        outfile=None):
    from matplotlib.ticker import NullFormatter
    if emb_method:
        if emb_method == "UMAP":
            from umap import UMAP
            proj = UMAP()
        else:
            import sklearn.manifold
            proj = getattr(sklearn.manifold, emb_method)()
        x, y = proj.fit_transform(emb).T
    else:
        x, y = emb.T
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(NullFormatter())
    for cls in set(classes):
        i = (classes == cls).nonzero()
        ax.scatter(x[i], y[i], label=cls, marker="o", s=1, alpha=1)
    if labels is not None:
        for i in range(len(emb)):
            if not i % 11:
                ax.annotate(labels[i], (x[i], y[i]), alpha=0.6, size=6)
    plt.axis('tight')
    plt.legend(loc='best', scatterpoints=1, markerscale=5, fontsize=10)
    if outfile:
        plt.savefig(str(outfile))
    else:
        plt.show()


def plot_dendrogram(dist, labels, outfile=None, method="centroid"):
    from scipy.cluster import hierarchy
    fig = plt.figure(figsize=(50, 45))
    # dendrogram
    axdendro = fig.add_axes([0.09, 0.1, 0.2, 0.8])
    axdendro.set_xticks([])
    axdendro.set_yticks([])
    Y = hierarchy.linkage(dist, method=method)
    Z = hierarchy.dendrogram(
        Y, orientation='right', labels=labels, leaf_font_size=10)
    # distance matrix
    index = Z['leaves']
    D = dist[index, :]
    D = D[:, index]
    axmatrix = fig.add_axes([0.3, 0.1, 0.6, 0.8])
    im = axmatrix.matshow(D, aspect='auto', origin='lower')
    axmatrix.set_xticks([])
    axmatrix.set_yticks([])
    # colorbar
    axcolor = fig.add_axes([0.91, 0.1, 0.02, 0.8])
    plt.colorbar(im, cax=axcolor)

    if outfile:
        fig.savefig(str(outfile))
    else:
        fig.show()
    plt.cla()


if __name__ == "__main__":
    plot_attention(
        "1 2 3 4".split(),
        "a b c d".split(),
        np.random.rand(4, 4),
        out_colors="r g b r".split())
