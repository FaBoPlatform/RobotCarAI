
;
input/batch_sizePlaceholder*
dtype0*
shape:
6
	step/stepConst*
dtype0*
valueB
 :���
�
queue/FIFOQueueFIFOQueueV2*
shared_name *
capacityd*
	container *
component_types
2*
shapes
::

queue/dequeue_opQueueDequeueManyV2queue/FIFOQueueinput/batch_size*
component_types
2*

timeout_ms���������
�
neural_network_model/Variable_1Const*
dtype0*�
value�B�"��t!?��?�l;?%IC>^ꖿ��<�V�?�;59����=�ݽ=XJ�?�����?����"<?9�U; g���|�����;�m�����<������n/��:>�?&��F����??Fw;��R��rc=
�
$neural_network_model/Variable_1/readIdentityneural_network_model/Variable_1*
T0*2
_class(
&$loc:@neural_network_model/Variable_1
x
neural_network_model/Variable_3Const*
dtype0*A
value8B6",����j��<�;�@���$����A���@ٙ�@l�0AC�AÃ��
�
$neural_network_model/Variable_3/readIdentityneural_network_model/Variable_3*
T0*2
_class(
&$loc:@neural_network_model/Variable_3
�
neural_network_model/Variable_5Const*
dtype0*�
value�B�"�?��I>?�e�>U+*�Yp���|4���6>DV��Z���A�?#����oҽo��#��M�@_LY��'�$�"�0g�=��?�-�>�?�>f1A0�����n@��{H鿻c�@o�R@k�<@�Z�~���?�c���@ˡ�>eGA��m�G����U��]�6�U�3����A��<�
�
$neural_network_model/Variable_5/readIdentityneural_network_model/Variable_5*
T0*2
_class(
&$loc:@neural_network_model/Variable_5
\
neural_network_model/Variable_7Const*
dtype0*%
valueB"uA�A˛�@�q��JgA
�
$neural_network_model/Variable_7/readIdentityneural_network_model/Variable_7*
T0*2
_class(
&$loc:@neural_network_model/Variable_7
�
neural_network_model/MatMulMatMulqueue/dequeue_op$neural_network_model/Variable_1/read*
transpose_b( *
T0*
transpose_a( 
k
neural_network_model/AddAddneural_network_model/MatMul$neural_network_model/Variable_3/read*
T0
D
neural_network_model/ReluReluneural_network_model/Add*
T0
�
neural_network_model/MatMul_1MatMulneural_network_model/Relu$neural_network_model/Variable_5/read*
transpose_b( *
T0*
transpose_a( 
r
neural_network_model/output_yAddneural_network_model/MatMul_1$neural_network_model/Variable_7/read*
T0
M
neural_network_model/scoreSoftmaxneural_network_model/output_y*
T0 