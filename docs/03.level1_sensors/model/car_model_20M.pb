
;
input/batch_sizePlaceholder*
dtype0*
shape:
6
	step/stepConst*
dtype0*
valueB
 :���	
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

timeout_ms���������*
component_types
2
�
neural_network_model/Variable_1Const*
dtype0*�
value�B�"��%?��?O�,?��Q>�9u�?([<v�t?a�L;���z�4>�=+?t?d�����s?p��1Q?��2<NꈿK��W�b<����>E=(���$���S
���!>;:�?\6����q?��<��D����<
�
$neural_network_model/Variable_1/readIdentityneural_network_model/Variable_1*
T0*2
_class(
&$loc:@neural_network_model/Variable_1
x
neural_network_model/Variable_3Const*
dtype0*A
value8B6",��x�<=<
@v�t�U,F���A���@J
�@��A>!�A��w�
�
$neural_network_model/Variable_3/readIdentityneural_network_model/Variable_3*
T0*2
_class(
&$loc:@neural_network_model/Variable_3
�
neural_network_model/Variable_5Const*
dtype0*�
value�B�"�	��!"?��>�X���3�>>������>��s¥����_?��ؾ|?'=�}5��B��&z@N�(���߿w�c?0>5T�?6�X�a��� ��@����>@*}̿� ̿��B@�@N@9"@�Gؿ�׿���?*iQ��͑@��S?��A���Iv��~��2�
��� �ilEAh��
�
$neural_network_model/Variable_5/readIdentityneural_network_model/Variable_5*
T0*2
_class(
&$loc:@neural_network_model/Variable_5
\
neural_network_model/Variable_7Const*
dtype0*%
valueB"c��Ap�@PsN��Z�@
�
$neural_network_model/Variable_7/readIdentityneural_network_model/Variable_7*
T0*2
_class(
&$loc:@neural_network_model/Variable_7
�
neural_network_model/MatMulMatMulqueue/dequeue_op$neural_network_model/Variable_1/read*
T0*
transpose_a( *
transpose_b( 
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