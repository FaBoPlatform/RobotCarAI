from nets import nets_factory
ssd_class = nets_factory.get_network('ssd_300_vgg')

ssd_params = ssd_class.default_params._replace(num_classes=5)
