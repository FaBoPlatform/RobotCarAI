import tensorflow as tf
from tensorflow.core.framework import graph_pb2
import copy

class LoadFrozenGraph():
    """
    LOAD FROZEN GRAPH
    ssd_movilenet_v1 300x300
    """
    def __init__(self, cfg):
        self.cfg = cfg
        return

    def load_graph(self):
        print('Building Graph')
        if not self.cfg['split_model']:
            return self.load_frozen_graph_without_split()
        else:
            return self.load_frozen_graph_with_split()

    def print_graph(self, graph):
        """
        PRINT GRAPH OPERATIONS
        """
        print("{:-^32}".format(" operations in graph "))
        for op in graph.get_operations():
            print(op.name,op.outputs)
        return

    def print_graph_def(self, graph_def):
        """
        PRINT GRAPHDEF NODE NAMES
        """
        print("{:-^32}".format(" nodes in graph_def "))
        for node in graph_def.node:
            print(node)
        return

    def print_graph_operation_by_name(self, graph, name):
        """
        PRINT GRAPH OPERATION DETAILS
        """
        op = graph.get_operation_by_name(name=name)
        print("{:-^32}".format(" operations in graph "))
        print("{:-^32}\n{}".format(" op ", op))
        print("{:-^32}\n{}".format(" op.name ", op.name))
        print("{:-^32}\n{}".format(" op.outputs ", op.outputs))
        print("{:-^32}\n{}".format(" op.inputs ", op.inputs))
        print("{:-^32}\n{}".format(" op.device ", op.device))
        print("{:-^32}\n{}".format(" op.graph ", op.graph))
        print("{:-^32}\n{}".format(" op.values ", op.values()))
        print("{:-^32}\n{}".format(" op.op_def ", op.op_def))
        print("{:-^32}\n{}".format(" op.colocation_groups ", op.colocation_groups))
        print("{:-^32}\n{}".format(" op.get_attr ", op.get_attr("T")))
        i = 0
        for output in op.outputs:
            op_tensor = output
            tensor_shape = op_tensor.get_shape().as_list()
            print("{:-^32}\n{}".format(" outputs["+str(i)+"] shape ", tensor_shape))
            i += 1
        print("{:-^32}\n{}".format(" op.name ", op.name))
        print("{:-^32}\n{}".format(" op.name ", op.name))
        return

    # helper function for split model
    def node_name(self, n):
        if n.startswith("^"):
            return n[1:]
        else:
            return n.split(":")[0]

    def load_frozen_graph_without_split(self):
        """
        Load frozen_graph.
        """
        model_path = self.cfg['model_path']
        debug_mode = self.cfg['debug_mode']

        detection_graph = tf.Graph()
        with detection_graph.as_default():
            graph_def = tf.GraphDef()
            with tf.gfile.GFile(model_path, 'rb') as fid:
                serialized_graph = fid.read()
                graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(graph_def, name='')
        """
        return
        """
        return detection_graph

    def load_frozen_graph_with_split(self):
        """
        Load frozen_graph and split it into half of GPU and CPU.
        """
        model_path = self.cfg['model_path']
        allow_memory_growth = self.cfg['allow_memory_growth']
        debug_mode = self.cfg['debug_mode']
        ssd_shape = self.cfg['ssd_shape']
        num_classes = self.cfg['num_classes']

        SPLIT_TARGET_SCORE_NAME = "Postprocessor/convert_scores"
        SPLIT_TARGET_EXPAND_NAME = "Postprocessor/ExpandDims_1"

        tf.reset_default_graph()
        if ssd_shape == 600:
            shape = 7326
        else:
            shape = 1917
        """ ADD CPU INPUT """
        score = tf.placeholder(tf.float32, shape=(None, shape, num_classes), name=SPLIT_TARGET_SCORE_NAME)
        expand = tf.placeholder(tf.float32, shape=(None, shape, 1, 4), name=SPLIT_TARGET_EXPAND_NAME)

        """
        Load placeholder's graph_def.
        """
        for node in tf.get_default_graph().as_graph_def().node:
            if node.name == SPLIT_TARGET_SCORE_NAME:
                score_def = node
            if node.name == SPLIT_TARGET_EXPAND_NAME:
                expand_def = node

        tf.reset_default_graph()

        graph_def = tf.GraphDef()
        with tf.gfile.GFile(model_path, 'rb') as fid:
            serialized_graph = fid.read()
            graph_def.ParseFromString(serialized_graph)
            dest_nodes = [SPLIT_TARGET_SCORE_NAME, SPLIT_TARGET_EXPAND_NAME]

            edges = {}
            name_to_node_map = {}
            node_seq = {}
            seq = 0
            for node in graph_def.node:
                n = self.node_name(node.name)
                name_to_node_map[n] = node
                edges[n] = [self.node_name(x) for x in node.input]
                node_seq[n] = seq
                seq += 1

            for d in dest_nodes:
                assert d in name_to_node_map, "%s is not in graph" % d

            nodes_to_keep = set()
            next_to_visit = dest_nodes

            while next_to_visit:
                n = next_to_visit[0]
                del next_to_visit[0]
                if n in nodes_to_keep:
                    continue
                nodes_to_keep.add(n)
                next_to_visit += edges[n]

            nodes_to_keep_list = sorted(list(nodes_to_keep), key=lambda n: node_seq[n])

            nodes_to_remove = set()
            for n in node_seq:
                if n in nodes_to_keep_list: continue
                nodes_to_remove.add(n)
            nodes_to_remove_list = sorted(list(nodes_to_remove), key=lambda n: node_seq[n])

            keep = graph_pb2.GraphDef()
            for n in nodes_to_keep_list:
                keep.node.extend([copy.deepcopy(name_to_node_map[n])])

            remove = graph_pb2.GraphDef()
            remove.node.extend([score_def])
            remove.node.extend([expand_def])
            for n in nodes_to_remove_list:
                remove.node.extend([copy.deepcopy(name_to_node_map[n])])

            with tf.device('/gpu:0'):
                tf.import_graph_def(keep, name='')
            with tf.device('/cpu:0'):
                tf.import_graph_def(remove, name='')

            #self.print_graph_operation_by_name(tf.get_default_graph(), SPLIT_TARGET_SCORE_NAME)
            #self.print_graph_operation_by_name(tf.get_default_graph(), SPLIT_TARGET_EXPAND_NAME)

        """
        return    
        """
        return tf.get_default_graph()
